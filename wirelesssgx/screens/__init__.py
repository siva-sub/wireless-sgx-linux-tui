"""TUI screens for Wireless@SGx"""

from .welcome import WelcomeScreen
from .register import RegisterScreen
from .otp import OTPScreen
from .success import SuccessScreen
from .credentials import CredentialsScreen
from .autoconnect import AutoConnectScreen

__all__ = ["WelcomeScreen", "RegisterScreen", "OTPScreen", "SuccessScreen", "CredentialsScreen", "AutoConnectScreen"]