#!/usr/bin/env python3
"""Debug test script for WirelessSGX TUI issues"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("WirelessSGX TUI Debug Test")
    print("=" * 50)
    
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
    
    print("\nTest scenarios:")
    print("1. Start app")
    print("2. Click 'New Registration'")  
    print("3. Click 'Back' to return to main screen")
    print("4. Try clicking buttons again")
    print("\nWatch for:")
    print("- Buttons becoming unclickable")
    print("- Screen navigation issues")
    print("- Focus problems")
    print("\nStarting TUI with debug logging...")
    print("(Check the log file for detailed debug info)")
    print("\nPress Ctrl+C to exit and view logs")
    
    # Start the TUI
    from wirelesssgx.app import main
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDebug session ended.")
        
        # Show log files
        log_files = list(Path(".").glob("wirelesssgx_debug_*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            print(f"\nLatest log file: {latest_log}")
            print("Last 50 lines:")
            print("-" * 50)
            with open(latest_log) as f:
                lines = f.readlines()
                for line in lines[-50:]:
                    print(line.rstrip())
        else:
            print("No log files found.")

if __name__ == "__main__":
    main()