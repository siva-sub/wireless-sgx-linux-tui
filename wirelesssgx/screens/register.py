"""Registration screen for Wireless@SGx TUI"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Header, Footer, Input, Select, Label
from textual.screen import Screen
from textual.validation import Regex
import re


class RegisterScreen(Screen):
    """Registration form screen"""
    
    CSS = """
    RegisterScreen {
        align: center middle;
    }
    
    #register-container {
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
    
    .field-group {
        margin-bottom: 1;
    }
    
    Label {
        margin-bottom: 0;
    }
    
    Input {
        width: 100%;
    }
    
    Select {
        width: 100%;
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
    """
    
    def __init__(self, retrieve_mode: bool = False):
        super().__init__()
        self.retrieve_mode = retrieve_mode
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Static(
                    "🔐 Retrieve Existing Account" if self.retrieve_mode else "📝 New Registration",
                    id="title"
                ),
                Vertical(
                    Label("Mobile Number (65XXXXXXXX):"),
                    Input(
                        placeholder="Enter Singapore mobile number",
                        id="mobile",
                        validators=[
                            Regex(r"^65[0-9]{8}$", failure_description="Must be Singapore number (65XXXXXXXX)")
                        ]
                    ),
                    classes="field-group"
                ),
                Vertical(
                    Label("Date of Birth (DDMMYYYY):"),
                    Input(
                        placeholder="Enter date of birth",
                        id="dob",
                        validators=[
                            Regex(r"^[0-3][0-9][0-1][0-9][1-2][0-9]{3}$", failure_description="Must be DDMMYYYY format")
                        ]
                    ),
                    classes="field-group"
                ),
                Vertical(
                    Label("Select ISP:"),
                    Select(
                        [(line, line) for line in ["Singtel", "Starhub"]],
                        prompt="Choose your ISP",
                        id="isp"
                    ),
                    classes="field-group"
                ),
                Horizontal(
                    Button("Back", variant="default", id="back"),
                    Button("Continue", variant="primary", id="continue"),
                    id="button-container"
                ),
                Static("", id="error-message"),
                id="register-container"
            )
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Focus first input on mount"""
        self.query_one("#mobile").focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "continue":
            self.validate_and_continue()
    
    def validate_and_continue(self) -> None:
        """Validate inputs and proceed"""
        mobile_input = self.query_one("#mobile", Input)
        dob_input = self.query_one("#dob", Input)
        isp_select = self.query_one("#isp", Select)
        error_msg = self.query_one("#error-message", Static)
        
        # Clear previous error
        error_msg.update("")
        
        # Validate mobile
        if not mobile_input.is_valid:
            error_msg.update("Invalid mobile number format")
            mobile_input.focus()
            return
            
        # Validate DOB
        if not dob_input.is_valid:
            error_msg.update("Invalid date of birth format")
            dob_input.focus()
            return
            
        # Validate ISP selection
        if isp_select.value == Select.BLANK:
            error_msg.update("Please select an ISP")
            isp_select.focus()
            return
        
        # All valid, proceed to OTP screen
        registration_data = {
            "mobile": mobile_input.value,
            "dob": dob_input.value,
            "isp": isp_select.value.lower(),
            "retrieve_mode": self.retrieve_mode
        }
        
        self.app.push_screen("otp", registration_data=registration_data)