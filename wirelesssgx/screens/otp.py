"""OTP entry screen for Wireless@SGx TUI"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Header, Footer, Input, Label, LoadingIndicator
from textual.screen import Screen
from textual.validation import Regex
from textual.reactive import reactive
from textual.timer import Timer
import asyncio
from typing import Dict, Optional

from ..core import WirelessSGXClient, WirelessSGXError


class OTPScreen(Screen):
    """OTP entry and validation screen"""
    
    CSS = """
    OTPScreen {
        align: center middle;
    }
    
    #otp-container {
        width: 60;
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
    
    #status {
        text-align: center;
        margin-bottom: 2;
    }
    
    #timer {
        text-align: center;
        color: $warning;
        margin-bottom: 1;
    }
    
    .field-group {
        margin-bottom: 1;
        align: center middle;
    }
    
    #otp-input {
        width: 20;
        text-align: center;
    }
    
    #button-container {
        margin-top: 2;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    
    #error-message {
        color: $error;
        text-align: center;
        margin-top: 1;
    }
    
    #loading {
        align: center middle;
    }
    """
    
    time_remaining = reactive(300)  # 5 minutes
    
    def __init__(self, registration_data: Dict):
        super().__init__()
        self.registration_data = registration_data
        self.client = WirelessSGXClient(registration_data["isp"])
        self.success_code: Optional[str] = None
        self.timer: Optional[Timer] = None
        self.requesting = False
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Static("📱 Enter OTP", id="title"),
                Static(f"OTP has been sent to {self.registration_data['mobile'].lstrip('65')}", id="status"),
                Static(self._format_time(), id="timer"),
                Vertical(
                    Label("Enter 6-digit OTP:"),
                    Input(
                        placeholder="XXXXXX",
                        id="otp-input",
                        max_length=6,
                        validators=[
                            Regex(r"^[0-9]{6}$", failure_description="Must be 6 digits")
                        ]
                    ),
                    classes="field-group"
                ),
                Horizontal(
                    Button("Back", variant="default", id="back"),
                    Button("Verify", variant="primary", id="verify"),
                    Button("Resend OTP", variant="warning", id="resend"),
                    id="button-container"
                ),
                Static("", id="error-message"),
                id="otp-container"
            )
        )
        yield Footer()
    
    async def on_mount(self) -> None:
        """Start OTP request and timer on mount"""
        self.query_one("#otp-input").focus()
        await self.request_otp()
        self.timer = self.set_interval(1, self.update_timer)
    
    def on_unmount(self) -> None:
        """Clean up timer"""
        if self.timer:
            self.timer.stop()
    
    def _format_time(self) -> str:
        """Format time remaining"""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        return f"⏱️ Time remaining: {minutes:02d}:{seconds:02d}"
    
    def update_timer(self) -> None:
        """Update countdown timer"""
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.query_one("#timer").update(self._format_time())
        else:
            self.query_one("#timer").update("⏱️ OTP expired - please resend")
            if self.timer:
                self.timer.stop()
    
    async def request_otp(self) -> None:
        """Request OTP from server"""
        if self.requesting:
            return
            
        self.requesting = True
        error_msg = self.query_one("#error-message", Static)
        error_msg.update("Requesting OTP...")
        
        try:
            # Run in thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.success_code = await loop.run_in_executor(
                None,
                self.client.request_registration,
                self.registration_data["mobile"],
                self.registration_data["dob"],
                "Dr", "User", "f", "SG", "user@example.com",
                self.registration_data["retrieve_mode"]
            )
            
            error_msg.update("")
            self.query_one("#status").update(
                f"✅ OTP sent to {self.registration_data['mobile'].lstrip('65')}"
            )
            
            # Reset timer
            self.time_remaining = 300
            
        except WirelessSGXError as e:
            error_msg.update(f"Error: {str(e)}")
            if "registered before" in str(e).lower() and not self.registration_data["retrieve_mode"]:
                error_msg.update(f"{str(e)}\nTry 'Retrieve Existing Account' instead")
        except Exception as e:
            error_msg.update(f"Unexpected error: {str(e)}")
        finally:
            self.requesting = False
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "verify":
            self.verify_otp()
        elif event.button.id == "resend":
            asyncio.create_task(self.request_otp())
    
    async def verify_otp(self) -> None:
        """Verify OTP and get credentials"""
        otp_input = self.query_one("#otp-input", Input)
        error_msg = self.query_one("#error-message", Static)
        
        if not otp_input.is_valid:
            error_msg.update("Please enter a valid 6-digit OTP")
            otp_input.focus()
            return
        
        if not self.success_code:
            error_msg.update("No OTP request found. Please resend OTP.")
            return
        
        error_msg.update("Verifying OTP...")
        
        try:
            # Get encrypted credentials
            loop = asyncio.get_event_loop()
            encrypted_data = await loop.run_in_executor(
                None,
                self.client.validate_otp,
                self.registration_data["mobile"],
                self.registration_data["dob"],
                otp_input.value,
                self.success_code,
                self.registration_data["retrieve_mode"]
            )
            
            # Decrypt credentials
            username, password = await loop.run_in_executor(
                None,
                self.client.decrypt_credentials,
                encrypted_data,
                otp_input.value
            )
            
            # Success! Move to success screen
            credentials = {
                "username": username,
                "password": password,
                "isp": self.registration_data["isp"]
            }
            
            self.app.push_screen("success", credentials=credentials)
            
        except WirelessSGXError as e:
            error_msg.update(f"Verification failed: {str(e)}")
        except Exception as e:
            error_msg.update(f"Unexpected error: {str(e)}")