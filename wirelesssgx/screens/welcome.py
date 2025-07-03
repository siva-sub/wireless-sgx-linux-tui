"""Welcome screen for Wireless@SGx TUI"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Header, Footer
from textual.screen import Screen
import logging
import os

logger = logging.getLogger('wirelesssgx.welcome')
DEBUG_MODE = os.environ.get('WIRELESSSGX_DEBUG', '').lower() in ('1', 'true', 'yes', 'on')


class WelcomeScreen(Screen):
    """Welcome screen with options"""
    
    def __init__(self):
        super().__init__()
        if DEBUG_MODE:
            logger.info("WelcomeScreen initialized")
    
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
        if DEBUG_MODE:
            logger.info("WelcomeScreen.compose() called")
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
    
    async def on_mount(self) -> None:
        """Called when screen is mounted"""
        if DEBUG_MODE:
            logger.info("WelcomeScreen mounted")
            logger.info(f"Screen name: {self.name}")
            logger.info(f"Is current screen: {self.app.screen == self}")
            logger.info(f"Button states:")
            for button in self.query(Button):
                logger.info(f"  - {button.id}: enabled={not button.disabled}, focusable={button.focusable}")
    
    async def on_screen_resume(self) -> None:
        """Called when returning to this screen"""
        if DEBUG_MODE:
            logger.info("WelcomeScreen resumed (returned from another screen)")
            logger.info(f"Current focus: {self.app.focused}")
            logger.info(f"Screen stack size: {len(self.app.screen_stack)}")
            # Re-check button states
            for button in self.query(Button):
                logger.info(f"  - {button.id}: enabled={not button.disabled}, focusable={button.focusable}")
                # Force refresh
                button.refresh()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        try:
            button_id = event.button.id
            
            if DEBUG_MODE:
                logger.info(f"Button pressed: {button_id}")
                logger.info(f"Event details: {event}")
                logger.info(f"Button widget: {event.button}")
                logger.info(f"Button enabled: {not event.button.disabled}")
            
            if button_id == "new-registration":
                if DEBUG_MODE:
                    logger.info("Navigating to register screen (new registration)")
                await self.app.push_screen("register", retrieve_mode=False)
            elif button_id == "retrieve-account":
                if DEBUG_MODE:
                    logger.info("Navigating to register screen (retrieve account)")
                await self.app.push_screen("register", retrieve_mode=True)
            elif button_id == "auto-connect":
                if DEBUG_MODE:
                    logger.info("Calling auto-connect action")
                await self.app.action_auto_connect()
            elif button_id == "manage-credentials":
                if DEBUG_MODE:
                    logger.info("Navigating to credentials screen")
                await self.app.push_screen("credentials")
            elif button_id == "exit":
                if DEBUG_MODE:
                    logger.info("Exiting app")
                self.app.exit()
        except Exception as e:
            # Log error but don't crash
            if DEBUG_MODE:
                logger.error(f"Error handling button press: {str(e)}", exc_info=True)
            if hasattr(self.app, 'log'):
                self.app.log.error(f"Error handling button press: {str(e)}")
            self.app.bell()