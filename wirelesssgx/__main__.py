"""Main entry point for the wirelesssgx package."""

import sys
from .app import main
from .cli import cli

if __name__ == "__main__":
    # Check if CLI commands are being used
    if len(sys.argv) > 1:
        # Use Click CLI for commands
        cli()
    else:
        # Launch TUI app
        main()