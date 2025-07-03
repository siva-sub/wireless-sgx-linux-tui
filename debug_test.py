#!/usr/bin/env python3
"""Enhanced debug test script for WirelessSGX TUI button issues"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("WirelessSGX TUI Enhanced Debug Test")
    print("=" * 60)
    
    # Set debug mode
    os.environ['WIRELESSSGX_DEBUG'] = '1'
    
    # Check if package is installed
    try:
        import wirelesssgx
        print(f"✓ WirelessSGX package found: version {wirelesssgx.__version__}")
    except ImportError:
        print("✗ WirelessSGX package not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "wirelesssgx"])
        import wirelesssgx
        print(f"✓ WirelessSGX installed: version {wirelesssgx.__version__}")
    
    print("\n🔍 TARGETED BUTTON DEBUGGING TEST")
    print("=" * 60)
    print("REPRODUCTION STEPS:")
    print("1. Start app - buttons should work")
    print("2. Click 'New Registration' button")  
    print("3. Click 'Back' button to return")
    print("4. Try clicking 'New Registration' again")
    print("\n🐛 BUG: Step 4 button should be unclickable")
    print("\n📊 DEBUG FEATURES:")
    print("- Screen instance tracking (check for recreation)")
    print("- Button state monitoring (focus, enabled, etc.)")
    print("- Event handler verification")
    print("- Focus chain debugging")
    print("- Manual testing with Ctrl+D")
    print("\n⌨️  SPECIAL DEBUG KEYS:")
    print("- Ctrl+D: Manual button state inspection & test")
    print("- Ctrl+C: Exit and show logs")
    print("\n🚀 Starting enhanced debug session...")
    print("(Detailed logs will be saved to timestamped file)")
    
    # Start the TUI
    from wirelesssgx.app import main
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🔍 DEBUG SESSION ENDED - ANALYZING LOGS")
        print("=" * 60)
        
        # Show log files
        log_files = list(Path(".").glob("wirelesssgx_debug_*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            print(f"\n📋 Latest log file: {latest_log}")
            
            # Analyze logs for key patterns
            print("\n🔍 SEARCHING FOR KEY PATTERNS:")
            with open(latest_log) as f:
                content = f.read()
                
                # Look for screen instance changes
                if "Instance ID:" in content:
                    print("✓ Screen instance tracking found")
                    lines = content.split('\n')
                    instance_lines = [line for line in lines if "Instance ID:" in line]
                    print(f"📊 Screen instances: {len(set(instance_lines))}")
                    for line in instance_lines:
                        print(f"   {line.strip()}")
                
                # Look for button state changes
                if "BUTTON STATES" in content:
                    print("✓ Button state tracking found")
                
                # Look for event failures
                if "BUTTON PRESS EVENT RECEIVED" in content:
                    events = content.count("BUTTON PRESS EVENT RECEIVED")
                    print(f"✓ Button press events detected: {events}")
                else:
                    print("❌ No button press events found - this is the problem!")
                
                # Look for focus issues
                if "Current focus:" in content:
                    print("✓ Focus tracking found")
            
            print(f"\n📄 Last 30 lines of debug log:")
            print("-" * 50)
            with open(latest_log) as f:
                lines = f.readlines()
                for line in lines[-30:]:
                    print(line.rstrip())
                    
            print(f"\n💡 FULL LOG ANALYSIS:")
            print(f"📂 Open this file for complete analysis: {latest_log}")
        else:
            print("❌ No log files found - debug mode may not have activated.")

if __name__ == "__main__":
    main()