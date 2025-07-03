"""Main Wireless@SGx TUI Application"""

from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.screen import Screen
from textual.containers import Container, Vertical
import asyncio
from typing import Dict, Optional

from .screens import WelcomeScreen, RegisterScreen, OTPScreen, SuccessScreen
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
    
    def on_key(self, event) -> None:
        """Close on ESC"""
        if event.key == "escape":
            self.app.pop_screen()
    
    def on_click(self) -> None:
        """Close on click"""
        self.app.pop_screen()


class WirelessSGXApp(App):
    """Main TUI Application for Wireless@SGx"""
    
    CSS = """
    Screen {
        background: $background;
    }
    """
    
    SCREENS = {
        "welcome": WelcomeScreen,
        "manual_instructions": ManualInstructionsScreen,
    }
    
    def __init__(self):
        super().__init__()
        self.storage = SecureStorage()
        self.network_manager = NetworkManager()
    
    def on_mount(self) -> None:
        """Show welcome screen on start"""
        self.push_screen("welcome")
    
    def action_auto_connect(self) -> None:
        """Auto-connect with saved credentials"""
        asyncio.create_task(self._auto_connect())
    
    async def _auto_connect(self) -> None:
        """Attempt to auto-connect with saved credentials"""
        # Check for saved credentials
        creds = await asyncio.get_event_loop().run_in_executor(
            None,
            self.storage.get_credentials
        )
        
        if not creds:
            # No saved credentials
            await self.push_screen_wait(
                Screen(
                    Container(
                        Vertical(
                            Static("❌ No saved credentials found!", style="color: red; text-align: center;"),
                            Static("Please register or retrieve your account first.", style="text-align: center; margin-top: 1;"),
                            Static("[Press any key to continue]", style="text-align: center; margin-top: 2;"),
                            align="center middle"
                        ),
                        align="center middle"
                    )
                )
            )
            return
        
        # Show success screen with saved credentials
        self.push_screen("success", credentials=creds)
    
    def push_screen(self, screen: str | Screen, **kwargs) -> None:
        """Push a screen with parameters"""
        if screen == "register":
            self._push_screen(RegisterScreen(**kwargs))
        elif screen == "otp":
            self._push_screen(OTPScreen(**kwargs))
        elif screen == "success":
            self._push_screen(SuccessScreen(**kwargs))
        elif screen == "manual_instructions":
            self._push_screen(ManualInstructionsScreen(**kwargs))
        else:
            super().push_screen(screen)


def main():
    """Main entry point"""
    app = WirelessSGXApp()
    app.run()


if __name__ == "__main__":
    main()