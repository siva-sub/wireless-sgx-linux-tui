"""Auto-connect screen for Wireless@SGx TUI"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Button
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
        await self.auto_connect()
    
    async def auto_connect(self) -> None:
        """Perform the auto-connect"""
        try:
            status = self.query_one("#status-text", Static)
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
                status.update("✅ Network configured! Attempting to connect...", classes="success")
                
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
                        status.update("✅ Successfully connected to Wireless@SGx!", classes="success")
                    else:
                        status.update("✅ Network configured. Will connect when in range.", classes="success")
                except Exception:
                    status.update("✅ Network configured. Will connect when in range.", classes="success")
            else:
                status.update("❌ Failed to configure network", classes="error")
                
        except Exception as e:
            status.update(f"❌ Error: {str(e)}", classes="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        try:
            if event.button.id == "back":
                self.app.pop_screen()
        except Exception:
            pass