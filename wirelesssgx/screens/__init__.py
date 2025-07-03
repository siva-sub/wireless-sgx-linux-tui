"""TUI screens for Wireless@SGx"""

from .welcome import WelcomeScreen
from .register import RegisterScreen
from .otp import OTPScreen
from .success import SuccessScreen
from .credentials import CredentialsScreen

__all__ = ["WelcomeScreen", "RegisterScreen", "OTPScreen", "SuccessScreen", "CredentialsScreen"]