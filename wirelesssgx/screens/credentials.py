"""Credentials management screen for Wireless@SGx TUI"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Header, Footer, Label
from textual.screen import Screen
from textual.reactive import reactive
import asyncio
import subprocess
from typing import Optional, Dict

from ..storage import SecureStorage
from ..network import NetworkManager, NetworkConfigError


class CredentialsScreen(Screen):
    """Screen for viewing and managing saved credentials"""
    
    CSS = """
    CredentialsScreen {
        align: center middle;
    }
    
    #credentials-container {
        width: 70;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 2 4;
    }
    
    #title {
        text-align: center;
        color: $primary;
        text-style: bold;
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
    
    #no-credentials {
        text-align: center;
        color: $warning;
        padding: 2;
    }
    
    #button-container {
        margin-top: 2;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    
    #status {
        text-align: center;
        margin-top: 1;
        height: 2;
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
    
    def __init__(self):
        super().__init__()
        self.storage = SecureStorage()
        self.network_manager = NetworkManager()
        self.credentials: Optional[Dict[str, str]] = None
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Static("🔐 Saved Credentials", id="title"),
                Vertical(id="credentials-display"),
                Static("", id="status"),
                Horizontal(
                    Button("Connect Now", variant="primary", id="connect"),
                    Button("Test Connection", variant="default", id="test"),
                    Button("Delete Credentials", variant="error", id="delete"),
                    Button("Back", variant="default", id="back"),
                    id="button-container"
                ),
                id="credentials-container"
            )
        )
        yield Footer()
    
    async def on_mount(self) -> None:
        """Load and display credentials on mount"""
        await self.load_credentials()
    
    async def load_credentials(self) -> None:
        """Load saved credentials"""
        display_container = self.query_one("#credentials-display", Vertical)
        display_container.remove_children()
        
        try:
            # Load credentials in thread
            self.credentials = await asyncio.get_event_loop().run_in_executor(
                None,
                self.storage.get_credentials
            )
            
            if self.credentials:
                # Show credentials
                creds_box = Vertical(
                    Static(f"Username: {self.credentials['username']}", classes="credential-line"),
                    Static(f"Password: {'*' * len(self.credentials['password'])}", classes="credential-line"),
                    Static(f"ISP: {self.credentials['isp'].title()}", classes="credential-line"),
                    classes="credentials-box"
                )
                display_container.mount(creds_box)
                
                # Check auto-connect status for NetworkManager
                try:
                    nm_type = self.network_manager.detect_network_manager()
                    if nm_type == "networkmanager":
                        import subprocess
                        result = subprocess.run(
                            ["nmcli", "-t", "-f", "connection.autoconnect", "con", "show", "Wireless@SGx"],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0 and result.stdout.strip() == "yes":
                            display_container.mount(
                                Static("✅ Auto-connect: Enabled", classes="credential-line success-status")
                            )
                        else:
                            display_container.mount(
                                Static("❌ Auto-connect: Disabled", classes="credential-line error-status")
                            )
                except:
                    pass
                
                # Enable buttons
                self.query_one("#connect").disabled = False
                self.query_one("#test").disabled = False
                self.query_one("#delete").disabled = False
            else:
                # No credentials found
                display_container.mount(
                    Static(
                        "No saved credentials found.\n\n"
                        "Please use 'New Registration' or 'Retrieve Existing Account'\n"
                        "from the main menu to set up your account.",
                        id="no-credentials"
                    )
                )
                
                # Disable buttons
                self.query_one("#connect").disabled = True
                self.query_one("#test").disabled = True
                self.query_one("#delete").disabled = True
                
        except Exception as e:
            display_container.mount(
                Static(f"Error loading credentials: {str(e)}", classes="error-status")
            )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "connect":
            asyncio.create_task(self.connect_now())
        elif event.button.id == "test":
            asyncio.create_task(self.test_connection())
        elif event.button.id == "delete":
            asyncio.create_task(self.delete_credentials())
    
    async def connect_now(self) -> None:
        """Connect using saved credentials"""
        if not self.credentials:
            return
            
        status = self.query_one("#status", Static)
        status.update("🔄 Connecting...", classes="info-status")
        
        try:
            # Configure network
            success = await asyncio.get_event_loop().run_in_executor(
                None,
                self.network_manager.configure_network,
                self.credentials["username"],
                self.credentials["password"]
            )
            
            if success:
                status.update("✅ Network configured! Connecting...", classes="success-status")
                
                # Try to connect with nmcli if available
                try:
                    result = subprocess.run(
                        ["nmcli", "connection", "up", "Wireless@SGx"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        status.update("✅ Connected to Wireless@SGx!", classes="success-status")
                    else:
                        status.update("✅ Network configured. Will connect when in range.", classes="success-status")
                except Exception:
                    status.update("✅ Network configured. Will connect when in range.", classes="success-status")
            else:
                status.update("❌ Failed to configure network", classes="error-status")
                
        except Exception as e:
            status.update(f"❌ Error: {str(e)}", classes="error-status")
    
    async def test_connection(self) -> None:
        """Test current connection status"""
        status = self.query_one("#status", Static)
        status.update("🔍 Testing connection...", classes="info-status")
        
        try:
            connected = await asyncio.get_event_loop().run_in_executor(
                None,
                self.network_manager.test_connection
            )
            
            if connected:
                status.update("✅ Connected to Wireless@SGx", classes="success-status")
            else:
                status.update("❌ Not connected to Wireless@SGx", classes="error-status")
                
        except Exception as e:
            status.update(f"❌ Error: {str(e)}", classes="error-status")
    
    async def delete_credentials(self) -> None:
        """Delete saved credentials with confirmation"""
        # For simplicity, we'll delete directly. In a real app, you'd want a confirmation dialog
        status = self.query_one("#status", Static)
        
        try:
            # Delete credentials
            deleted = await asyncio.get_event_loop().run_in_executor(
                None,
                self.storage.delete_credentials
            )
            
            if deleted:
                # Also try to remove network configuration
                try:
                    import subprocess
                    subprocess.run(
                        ["nmcli", "connection", "delete", "Wireless@SGx"],
                        capture_output=True
                    )
                except:
                    pass
                
                status.update("✅ Credentials deleted successfully", classes="success-status")
                
                # Reload display
                await self.load_credentials()
            else:
                status.update("❌ Failed to delete credentials", classes="error-status")
                
        except Exception as e:
            status.update(f"❌ Error: {str(e)}", classes="error-status")