"""Welcome screen for Wireless@SGx TUI"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Header, Footer
from textual.screen import Screen


class WelcomeScreen(Screen):
    """Welcome screen with options"""
    
    CSS = """
    WelcomeScreen {
        align: center middle;
    }
    
    #welcome-container {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 2 4;
    }
    
    #logo {
        text-align: center;
        color: $primary;
        text-style: bold;
        margin-bottom: 2;
    }
    
    #description {
        text-align: center;
        margin-bottom: 3;
    }
    
    #button-container {
        align: center middle;
        height: auto;
    }
    
    Button {
        width: 40;
        margin: 1 0;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Static("🌐 Wireless@SGx Linux Setup", id="logo"),
                Static(
                    "Connect to Singapore's public WiFi network\n"
                    "with automatic configuration",
                    id="description"
                ),
                Vertical(
                    Button("New Registration", variant="primary", id="new-registration"),
                    Button("Retrieve Existing Account", variant="default", id="retrieve-account"),
                    Button("Auto-Connect (Saved Credentials)", variant="success", id="auto-connect"),
                    Button("Manage Credentials", variant="default", id="manage-credentials"),
                    Button("Exit", variant="error", id="exit"),
                    id="button-container"
                ),
                id="welcome-container"
            )
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        try:
            button_id = event.button.id
            
            if button_id == "new-registration":
                self.app.push_screen("register", retrieve_mode=False)
            elif button_id == "retrieve-account":
                self.app.push_screen("register", retrieve_mode=True)
            elif button_id == "auto-connect":
                self.app.action_auto_connect()
            elif button_id == "manage-credentials":
                self.app.push_screen("credentials")
            elif button_id == "exit":
                self.app.exit()
        except Exception as e:
            # Log error but don't crash
            if hasattr(self.app, 'log'):
                self.app.log.error(f"Error handling button press: {str(e)}")
            self.app.bell()