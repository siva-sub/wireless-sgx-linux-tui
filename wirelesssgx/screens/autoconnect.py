"""Auto-connect screen for Wireless@SGx TUI"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Button, LoadingIndicator
from textual.screen import Screen
import asyncio
from typing import Dict

from ..network import NetworkManager


class AutoConnectScreen(Screen):
    """Screen for auto-connecting with saved credentials"""
    
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
    
    #loading {
        margin: 1 0;
        align: center middle;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
    }
    
    #subtitle {
        text-align: center;
        margin-bottom: 2;
    }
    
    #back {
        margin-top: 2;
    }
    """
    
    def __init__(self, *, credentials: Dict[str, str]):
        super().__init__()
        self.credentials = credentials
        self.network_manager = NetworkManager()
        # Ensure we have required fields
        if not credentials or 'username' not in credentials or 'password' not in credentials:
            self.credentials = {'username': 'Unknown', 'password': ''}
        
    def compose(self) -> ComposeResult:
        yield Container(
            Vertical(
                Static("🔄 Auto-Connect", id="title"),
                Static(f"Using saved credentials for: {self.credentials['username']}", id="subtitle"),
                LoadingIndicator(id="loading"),
                Static("Configuring network...", id="status-text", classes="info"),
                Button("Back", id="back"),
                id="status-container"
            )
        )
    
    async def on_mount(self) -> None:
        """Start auto-connect process"""
        # Set a maximum timeout to ensure screen closes
        self.set_timer(10, self.dismiss)  # Auto-close after 10 seconds max
        await self.auto_connect()
    
    async def auto_connect(self) -> None:
        """Perform the auto-connect"""
        try:
            status = self.query_one("#status-text", Static)
            loading = self.query_one("#loading", LoadingIndicator)
        except Exception:
            return
        
        try:
            # Configure network
            success = await asyncio.get_event_loop().run_in_executor(
                None,
                self.network_manager.configure_network,
                self.credentials["username"],
                self.credentials["password"]
            )
            
            if success:
                status.update("✅ Network configured! Attempting to connect...")
                status.set_class(False, "success", "info", "error")
                status.add_class("success")
                try:
                    loading.remove()  # Hide loading indicator
                except:
                    pass
                
                # Try to connect with nmcli
                try:
                    import subprocess
                    await asyncio.sleep(1)
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: subprocess.run(
                            ["nmcli", "connection", "up", "Wireless@SGx"],
                            capture_output=True,
                            text=True
                        )
                    )
                    
                    if result.returncode == 0:
                        status.update("✅ Successfully connected to Wireless@SGx!")
                        status.set_class(False, "success", "info", "error")
                        status.add_class("success")
                        await asyncio.sleep(2)  # Show success message for 2 seconds
                        self.dismiss()  # Return to welcome screen
                    else:
                        status.update("✅ Network configured. Will connect when in range.")
                        status.set_class(False, "success", "info", "error")
                        status.add_class("success")
                        await asyncio.sleep(2)  # Show message for 2 seconds
                        self.dismiss()  # Return to welcome screen
                except Exception:
                    status.update("✅ Network configured. Will connect when in range.")
                    status.set_class(False, "success", "info", "error")
                    status.add_class("success")
                    await asyncio.sleep(2)  # Show message for 2 seconds
                    self.dismiss()  # Return to welcome screen
            else:
                status.update("❌ Failed to configure network")
                status.set_class(False, "success", "info", "error")
                status.add_class("error")
                await asyncio.sleep(2)  # Show error message for 2 seconds
                
        except Exception as e:
            try:
                status.update(f"❌ Error: {str(e)}")
                status.set_class(False, "success", "info", "error")
                status.add_class("error")
                await asyncio.sleep(2)  # Show error message for 2 seconds
            except:
                pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        try:
            if event.button.id == "back":
                self.dismiss()
        except Exception:
            pass