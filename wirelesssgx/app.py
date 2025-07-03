"""Main Wireless@SGx TUI Application"""

from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.screen import Screen
from textual.containers import Container, Vertical
import asyncio
from typing import Dict, Optional

from .screens import WelcomeScreen, RegisterScreen, OTPScreen, SuccessScreen, CredentialsScreen
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
        "register": RegisterScreen,
        "otp": OTPScreen,
        "success": SuccessScreen,
        "manual_instructions": ManualInstructionsScreen,
        "credentials": CredentialsScreen,
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
            self.push_screen(
                "manual_instructions",
                instructions="❌ No saved credentials found!\n\n"
                           "Please use 'New Registration' or 'Retrieve Existing Account'\n"
                           "to set up your Wireless@SGx account first."
            )
            return
        
        # Create auto-connect status screen
        class AutoConnectScreen(Screen):
            CSS = """
            AutoConnectScreen {
                align: center middle;
            }
            
            #status-container {
                width: 60;
                height: auto;
                border: thick $background 80%;
                background: $surface;
                padding: 2 4;
                align: center middle;
            }
            
            #status-text {
                text-align: center;
                margin-bottom: 2;
            }
            
            .success { color: $success; }
            .error { color: $error; }
            .info { color: $primary; }
            """
            
            def __init__(self, credentials: Dict[str, str]):
                super().__init__()
                self.credentials = credentials
                self.network_manager = NetworkManager()
                
            def compose(self) -> ComposeResult:
                yield Container(
                    Vertical(
                        Static("🔄 Auto-Connect", style="text-align: center; font-weight: bold; margin-bottom: 2;"),
                        Static(f"Using saved credentials for: {self.credentials['username']}", style="text-align: center; margin-bottom: 2;"),
                        Static("Configuring network...", id="status-text", classes="info"),
                        Button("Back", id="back", style="margin-top: 2;"),
                        id="status-container"
                    )
                )
            
            async def on_mount(self) -> None:
                """Start auto-connect process"""
                status = self.query_one("#status-text", Static)
                
                try:
                    # Configure network
                    success = await asyncio.get_event_loop().run_in_executor(
                        None,
                        self.network_manager.configure_network,
                        self.credentials["username"],
                        self.credentials["password"]
                    )
                    
                    if success:
                        status.update("✅ Network configured! Attempting to connect...", classes="success")
                        
                        # Try to connect with nmcli
                        try:
                            import subprocess
                            await asyncio.sleep(1)
                            result = await asyncio.get_event_loop().run_in_executor(
                                None,
                                subprocess.run,
                                ["nmcli", "connection", "up", "Wireless@SGx"],
                                {"capture_output": True, "text": True}
                            )
                            
                            if result.returncode == 0:
                                status.update("✅ Successfully connected to Wireless@SGx!", classes="success")
                            else:
                                status.update("✅ Network configured. Will connect when in range.", classes="success")
                        except:
                            status.update("✅ Network configured. Will connect when in range.", classes="success")
                    else:
                        status.update("❌ Failed to configure network", classes="error")
                        
                except Exception as e:
                    status.update(f"❌ Error: {str(e)}", classes="error")
            
            def on_button_pressed(self, event: Button.Pressed) -> None:
                if event.button.id == "back":
                    self.app.pop_screen()
        
        # Show auto-connect screen
        self.push_screen(AutoConnectScreen(creds))
    
    def push_screen(self, screen: str | Screen, **kwargs) -> None:
        """Push a screen with parameters"""
        if isinstance(screen, str) and screen in self.SCREENS:
            screen_instance = self.SCREENS[screen](**kwargs)
            super().push_screen(screen_instance)
        else:
            super().push_screen(screen)


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