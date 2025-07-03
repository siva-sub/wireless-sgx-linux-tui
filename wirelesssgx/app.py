"""Main Wireless@SGx TUI Application"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Button
from textual.screen import Screen
from textual.containers import Container, Vertical
import asyncio
from typing import Dict, Optional

from .screens import WelcomeScreen, RegisterScreen, OTPScreen, SuccessScreen, CredentialsScreen, AutoConnectScreen
from .storage import SecureStorage
from .network import NetworkManager


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
    
    def __init__(self, instructions: str):
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
    
    async def on_mount(self) -> None:
        """Show welcome screen on start"""
        await self.push_screen("welcome")
    
    async def action_auto_connect(self) -> None:
        """Auto-connect with saved credentials"""
        try:
            # Check for saved credentials
            creds = self.storage.get_credentials()
            
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
                if screen in self.SCREENS:
                    # Debug: Log screen instantiation
                    if hasattr(self, 'log'):
                        self.log.info(f"Creating screen '{screen}' with kwargs: {kwargs}")
                    
                    screen_class = self.SCREENS[screen]
                    
                    # Special handling for screens that need parameters
                    if screen == "autoconnect" and "credentials" not in kwargs:
                        raise ValueError("AutoConnectScreen requires 'credentials' parameter")
                    
                    screen_instance = screen_class(**kwargs)
                    await super().push_screen(screen_instance)
                else:
                    # Screen not found, show error
                    self.bell()
                    if hasattr(self, 'log'):
                        self.log.error(f"Screen '{screen}' not found in SCREENS dictionary")
                    raise ValueError(f"Unknown screen: {screen}")
            else:
                await super().push_screen(screen)
        except Exception as e:
            # Handle any errors during screen creation or pushing
            import traceback
            error_trace = traceback.format_exc()
            
            self.bell()
            if hasattr(self, 'log'):
                self.log.error(f"Error pushing screen: {str(e)}\n{error_trace}")
            
            # Try to show error in manual instructions screen
            try:
                error_screen = ManualInstructionsScreen(
                    instructions=f"❌ Error loading screen:\n\n{str(e)}\n\n"
                               f"Error Type: {type(e).__name__}\n\n"
                               f"Stack Trace:\n{error_trace}\n\n"
                               "Please report this issue if it persists."
                )
                await super().push_screen(error_screen)
            except:
                pass  # Last resort - don't crash the app


def main():
    """Main entry point"""
    import sys
    
    # Check if CLI commands are being used
    if len(sys.argv) > 1:
        from .cli import cli
        cli()
    else:
        # Launch TUI app
        app = WirelessSGXApp()
        app.run()


if __name__ == "__main__":
    main()