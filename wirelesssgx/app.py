"""Main Wireless@SGx TUI Application"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Button
from textual.screen import Screen
from textual.containers import Container, Vertical
import asyncio
from typing import Dict, Optional
import logging
import os
import sys
from datetime import datetime

from .screens import WelcomeScreen, RegisterScreen, OTPScreen, SuccessScreen, CredentialsScreen, AutoConnectScreen
from .storage import SecureStorage
from .network import NetworkManager

# Set up debug logging
DEBUG_MODE = os.environ.get('WIRELESSSGX_DEBUG', '').lower() in ('1', 'true', 'yes', 'on')

if DEBUG_MODE:
    log_file = f"wirelesssgx_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stderr)
        ]
    )
    logger = logging.getLogger('wirelesssgx')
    logger.info(f"Debug mode enabled. Logging to {log_file}")
else:
    logger = logging.getLogger('wirelesssgx')
    logger.setLevel(logging.WARNING)


class ManualInstructionsScreen(Screen):
    """Screen to show manual configuration instructions"""
    
    CSS = """
    ManualInstructionsScreen {
        align: center middle;
    }
    
    #instructions-container {
        width: 80;
        height: 80%;
        border: thick $background 80%;
        background: $surface;
        padding: 2 4;
        overflow-y: auto;
    }
    
    #instructions {
        margin: 1;
    }
    
    #close-button {
        dock: bottom;
        height: 3;
        align: center middle;
    }
    """
    
    def __init__(self, *, instructions: str):
        super().__init__()
        self.instructions = instructions
        
    def compose(self) -> ComposeResult:
        yield Container(
            Vertical(
                Static(self.instructions, id="instructions"),
                Static("[Press ESC or click to close]", id="close-button"),
                id="instructions-container"
            )
        )
    
    async def on_key(self, event) -> None:
        """Close on ESC"""
        if event.key == "escape":
            await self.app.pop_screen()
    
    async def on_click(self) -> None:
        """Close on click"""
        await self.app.pop_screen()


class WirelessSGXApp(App):
    """Main TUI Application for Wireless@SGx"""
    
    CSS = """
    Screen {
        background: $background;
    }
    """
    
    SCREENS = {
        "welcome": WelcomeScreen,
        "register": RegisterScreen,
        "otp": OTPScreen,
        "success": SuccessScreen,
        "manual_instructions": ManualInstructionsScreen,
        "credentials": CredentialsScreen,
        "autoconnect": AutoConnectScreen,
    }
    
    def __init__(self):
        super().__init__()
        self.storage = SecureStorage()
        self.network_manager = NetworkManager()
        self.debug_mode = DEBUG_MODE
        if self.debug_mode:
            logger.info("WirelessSGXApp initialized in debug mode")
    
    async def on_mount(self) -> None:
        """Show welcome screen on start"""
        if self.debug_mode:
            logger.info("App mounted, pushing welcome screen")
        await self.push_screen("welcome")
    
    async def action_auto_connect(self) -> None:
        """Auto-connect with saved credentials"""
        if self.debug_mode:
            logger.info("action_auto_connect called")
        
        try:
            # Check for saved credentials
            creds = self.storage.get_credentials()
            
            if self.debug_mode:
                logger.info(f"Retrieved credentials: {bool(creds)}")
            
            if not creds:
                # No saved credentials
                await self.push_screen(
                    "manual_instructions",
                    instructions="❌ No saved credentials found!\n\n"
                               "Please use 'New Registration' or 'Retrieve Existing Account'\n"
                               "to set up your Wireless@SGx account first."
                )
                return
            
            # Show auto-connect screen using the registered screen
            await self.push_screen("autoconnect", credentials=creds)
            
        except Exception as e:
            # Handle any errors gracefully with detailed error info
            import traceback
            error_details = traceback.format_exc()
            
            if self.debug_mode:
                logger.error(f"Error in action_auto_connect: {str(e)}")
                logger.error(f"Full traceback:\n{error_details}")
            
            await self.push_screen(
                "manual_instructions", 
                instructions=f"❌ Error during auto-connect:\n\n{str(e)}\n\n"
                           f"Error Type: {type(e).__name__}\n\n"
                           f"Details:\n{error_details}\n\n"
                           "Please try again or use manual connection methods."
            )
    
    
    async def push_screen(self, screen: str | Screen, **kwargs) -> None:
        """Push a screen with parameters"""
        try:
            if isinstance(screen, str):
                if self.debug_mode:
                    logger.info(f"push_screen called with: screen='{screen}', kwargs={kwargs}")
                    logger.info(f"Current screen stack size: {len(self.screen_stack)}")
                    logger.info(f"Current screen: {self.screen.__class__.__name__}")
                
                if screen in self.SCREENS:
                    screen_class = self.SCREENS[screen]
                    
                    # Special handling for screens that need parameters
                    if screen == "autoconnect" and "credentials" not in kwargs:
                        raise ValueError("AutoConnectScreen requires 'credentials' parameter")
                    
                    if self.debug_mode:
                        logger.info(f"Creating instance of {screen_class.__name__} with kwargs: {kwargs}")
                    
                    screen_instance = screen_class(**kwargs)
                    
                    if self.debug_mode:
                        logger.info(f"Screen instance created successfully: {screen_instance}")
                        logger.info("Calling super().push_screen()")
                    
                    await super().push_screen(screen_instance)
                    
                    if self.debug_mode:
                        logger.info(f"Screen pushed successfully. New stack size: {len(self.screen_stack)}")
                else:
                    # Screen not found, show error
                    self.bell()
                    error_msg = f"Unknown screen: {screen}"
                    if self.debug_mode:
                        logger.error(error_msg)
                    raise ValueError(error_msg)
            else:
                if self.debug_mode:
                    logger.info(f"Pushing screen instance directly: {screen.__class__.__name__}")
                await super().push_screen(screen)
        except Exception as e:
            # Handle any errors during screen creation or pushing
            import traceback
            error_trace = traceback.format_exc()
            
            if self.debug_mode:
                logger.error(f"Error in push_screen: {str(e)}")
                logger.error(f"Full traceback:\n{error_trace}")
            
            self.bell()
            
            # Try to show error in manual instructions screen
            try:
                error_screen = ManualInstructionsScreen(
                    instructions=f"❌ Error loading screen:\n\n{str(e)}\n\n"
                               f"Error Type: {type(e).__name__}\n\n"
                               f"Stack Trace:\n{error_trace}\n\n"
                               "Please report this issue if it persists."
                )
                await super().push_screen(error_screen)
            except Exception as nested_e:
                if self.debug_mode:
                    logger.error(f"Failed to show error screen: {nested_e}")
    
    async def pop_screen(self) -> None:
        """Override pop_screen to add debugging"""
        if self.debug_mode:
            logger.info(f"pop_screen called. Current stack size: {len(self.screen_stack)}")
            logger.info(f"Current screen: {self.screen.__class__.__name__}")
            if len(self.screen_stack) > 1:
                logger.info(f"Will return to: {self.screen_stack[-2].__class__.__name__}")
        
        result = await super().pop_screen()
        
        if self.debug_mode:
            logger.info(f"After pop_screen. New stack size: {len(self.screen_stack)}")
            logger.info(f"Current screen: {self.screen.__class__.__name__}")
            logger.info(f"Current focus: {self.focused}")
        
        return result


def main():
    """Main entry point"""
    import sys
    
    # Check for debug flag
    if '--debug' in sys.argv:
        os.environ['WIRELESSSGX_DEBUG'] = '1'
        sys.argv.remove('--debug')
        print("Debug mode enabled. Check log file for details.")
    
    # Check if CLI commands are being used
    if len(sys.argv) > 1:
        from .cli import cli
        cli()
    else:
        # Launch TUI app
        app = WirelessSGXApp()
        if DEBUG_MODE:
            print(f"Starting WirelessSGX TUI in debug mode. Log file: wirelesssgx_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        app.run()


if __name__ == "__main__":
    main()