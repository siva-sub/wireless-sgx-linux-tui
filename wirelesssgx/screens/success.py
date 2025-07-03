"""Success screen for Wireless@SGx TUI"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Header, Footer, Label
from textual.screen import Screen
from typing import Dict
import asyncio

from ..network import NetworkManager, NetworkConfigError
from ..storage import SecureStorage


class SuccessScreen(Screen):
    """Success screen showing credentials and network configuration"""
    
    CSS = """
    SuccessScreen {
        align: center middle;
    }
    
    #success-container {
        width: 70;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 2 4;
    }
    
    #title {
        text-align: center;
        color: $success;
        text-style: bold;
        margin-bottom: 2;
    }
    
    #status {
        text-align: center;
        margin-bottom: 2;
    }
    
    .credentials-box {
        border: solid $primary;
        padding: 1 2;
        margin-bottom: 2;
        background: $panel;
    }
    
    .credential-line {
        margin: 0.5 0;
    }
    
    #button-container {
        margin-top: 2;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    
    #network-status {
        text-align: center;
        margin-top: 1;
    }
    
    .success-status {
        color: $success;
    }
    
    .error-status {
        color: $error;
    }
    
    .info-status {
        color: $primary;
    }
    """
    
    def __init__(self, credentials: Dict[str, str]):
        super().__init__()
        self.credentials = credentials
        self.network_manager = NetworkManager()
        self.storage = SecureStorage()
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Static("✅ Registration Successful!", id="title"),
                Static("Your Wireless@SGx credentials:", id="status"),
                Vertical(
                    Static(f"SSID: Wireless@SGx", classes="credential-line"),
                    Static(f"Username: {self.credentials['username']}", classes="credential-line"),
                    Static(f"Password: {self.credentials['password']}", classes="credential-line"),
                    Static(f"ISP: {self.credentials['isp'].title()}", classes="credential-line"),
                    classes="credentials-box"
                ),
                Static("", id="network-status"),
                Horizontal(
                    Button("Show Manual Instructions", variant="default", id="manual"),
                    Button("View Credentials", variant="default", id="view-creds"), 
                    Button("Done", variant="success", id="done"),
                    id="button-container"
                ),
                id="success-container"
            )
        )
        yield Footer()
    
    async def on_mount(self) -> None:
        """Save credentials and auto-connect on mount"""
        # First save credentials
        try:
            saved = await asyncio.get_event_loop().run_in_executor(
                None,
                self.storage.save_credentials,
                self.credentials["username"],
                self.credentials["password"],
                self.credentials["isp"]
            )
            
            if saved:
                self.query_one("#network-status").update(
                    "💾 Credentials saved securely. Auto-connecting...",
                    classes="info-status"
                )
                # Auto-connect after saving
                await asyncio.sleep(1)
                await self.configure_network()
            else:
                self.query_one("#network-status").update(
                    "⚠️ Could not save credentials",
                    classes="error-status"
                )
        except Exception as e:
            self.query_one("#network-status").update(
                f"⚠️ Could not save credentials: {str(e)}",
                classes="error-status"
            )
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        try:
            if event.button.id == "manual":
                await self.show_manual_instructions()
            elif event.button.id == "view-creds":
                await self.app.push_screen("credentials")
            elif event.button.id == "done":
                self.app.exit()
        except Exception as e:
            # Log error but don't crash
            try:
                status = self.query_one("#network-status")
                status.update(f"❌ Error: {str(e)}", classes="error-status")
            except:
                pass
    
    async def configure_network(self) -> None:
        """Configure network automatically"""
        status_widget = self.query_one("#network-status")
        status_widget.update("🔧 Configuring network...", classes="info-status")
        
        try:
            # Run configuration in thread
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self.network_manager.configure_network,
                self.credentials["username"],
                self.credentials["password"]
            )
            
            if success:
                status_widget.update(
                    "✅ Network configured successfully! You should be connected soon.",
                    classes="success-status"
                )
                
                # Test connection after a delay
                await asyncio.sleep(3)
                connected = await loop.run_in_executor(
                    None,
                    self.network_manager.test_connection
                )
                
                if connected:
                    status_widget.update(
                        "🌐 Connected to Wireless@SGx!",
                        classes="success-status"
                    )
            else:
                status_widget.update(
                    "❌ Auto-configuration failed. Use manual instructions.",
                    classes="error-status"
                )
                
        except NetworkConfigError as e:
            status_widget.update(
                f"❌ Configuration error: {str(e)}",
                classes="error-status"
            )
        except Exception as e:
            status_widget.update(
                f"❌ Unexpected error: {str(e)}",
                classes="error-status"
            )
    
    async def show_manual_instructions(self) -> None:
        """Show manual configuration instructions"""
        instructions = self.network_manager.get_manual_config_instructions(
            self.credentials["username"],
            self.credentials["password"]
        )
        
        # Create a popup or new screen with instructions
        await self.app.push_screen("manual_instructions", instructions=instructions)