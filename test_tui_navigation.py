#!/usr/bin/env python3
"""Test script to verify TUI navigation works properly"""

import sys
import os

# Add the parent directory to the path so we can import wirelesssgx
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wirelesssgx.app import WirelessSGXApp
from wirelesssgx.storage import SecureStorage


def test_screens_registered():
    """Test that all screens are properly registered"""
    app = WirelessSGXApp()
    
    expected_screens = [
        "welcome",
        "register", 
        "otp",
        "success",
        "manual_instructions",
        "credentials",
        "autoconnect"  # This was missing before
    ]
    
    print("Checking registered screens...")
    for screen in expected_screens:
        if screen in app.SCREENS:
            print(f"✅ {screen}: registered")
        else:
            print(f"❌ {screen}: NOT registered")
    
    print(f"\nTotal screens registered: {len(app.SCREENS)}")
    print(f"Screens: {list(app.SCREENS.keys())}")


def test_auto_connect_navigation():
    """Test that auto-connect navigation works"""
    print("\n\nTesting auto-connect navigation...")
    
    # Create a test app instance
    app = WirelessSGXApp()
    
    # Check if the action exists
    if hasattr(app, 'action_auto_connect'):
        print("✅ action_auto_connect method exists")
    else:
        print("❌ action_auto_connect method missing")
    
    # Check if _auto_connect exists
    if hasattr(app, '_auto_connect'):
        print("✅ _auto_connect method exists")
    else:
        print("❌ _auto_connect method missing")
    
    # Check storage
    if hasattr(app, 'storage') and isinstance(app.storage, SecureStorage):
        print("✅ SecureStorage is initialized")
    else:
        print("❌ SecureStorage not properly initialized")


def test_push_screen_error_handling():
    """Test that push_screen has proper error handling"""
    print("\n\nTesting push_screen error handling...")
    
    app = WirelessSGXApp()
    
    # Try to push a non-existent screen
    try:
        app.push_screen("non_existent_screen")
        print("❌ push_screen did not handle non-existent screen properly")
    except:
        print("✅ push_screen properly handles non-existent screens")
    
    # Try to push with invalid parameters
    try:
        app.push_screen("register", invalid_param="test")
        # This should work because the screen might ignore extra params
        print("✅ push_screen handles extra parameters gracefully")
    except:
        print("⚠️  push_screen raised error on extra parameters")


if __name__ == "__main__":
    print("=" * 60)
    print("Wireless@SGX TUI Navigation Test")
    print("=" * 60)
    
    test_screens_registered()
    test_auto_connect_navigation()
    test_push_screen_error_handling()
    
    print("\n" + "=" * 60)
    print("Test complete! You can now run 'wirelesssgx' to test the TUI.")
    print("=" * 60)