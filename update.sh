#!/bin/bash

# Wireless@SGx Linux TUI Updater
# Author: Sivasubramanian Ramanathan
# Repository: https://github.com/siva-sub/wireless-sgx-linux-tui

set -e

echo "🔄 Wireless@SGx Linux TUI Updater"
echo "================================="
echo

# Colors
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
NC=$'\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}Error: This updater is for Linux only${NC}"
    exit 1
fi

# Detect installation method
echo "Detecting installation..."

# Check if installed in virtual environment
if [ -d ~/.wirelesssgx-venv ]; then
    echo -e "${GREEN}✓ Virtual environment installation detected${NC}"
    source ~/.wirelesssgx-venv/bin/activate
    VENV_INSTALL=true
else
    VENV_INSTALL=false
fi

# Update from PyPI or GitHub
echo
echo "Update method:"
echo "1) Update from PyPI (stable)"
echo "2) Update from GitHub (latest)"
read -p "Choose [1-2]: " update_method < /dev/tty

case $update_method in
    1)
        echo "Updating from PyPI..."
        pip install --upgrade wirelesssgx
        ;;
    2)
        echo "Updating from GitHub..."
        pip install --upgrade git+https://github.com/siva-sub/wireless-sgx-linux-tui.git
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Update desktop entry if needed
if [ -f ~/.local/share/applications/wirelesssgx.desktop ]; then
    echo
    echo "Updating desktop entry..."
    
    # Check if wrapper script needs updating
    if [ "$VENV_INSTALL" = true ] && [ ! -f ~/.local/bin/wirelesssgx-launcher ]; then
        mkdir -p ~/.local/bin
        cat > ~/.local/bin/wirelesssgx-launcher << 'EOF'
#!/bin/bash
source ~/.wirelesssgx-venv/bin/activate
exec wirelesssgx "$@"
EOF
        chmod +x ~/.local/bin/wirelesssgx-launcher
        
        # Update desktop entry to use wrapper
        sed -i 's|Exec=wirelesssgx|Exec=/home/'$USER'/.local/bin/wirelesssgx-launcher|' ~/.local/share/applications/wirelesssgx.desktop
        echo -e "${GREEN}✓ Desktop entry updated${NC}"
    fi
fi

# Show version
echo
echo -e "${GREEN}✅ Update complete!${NC}"
echo
if [ "$VENV_INSTALL" = true ]; then
    python -c "import wirelesssgx; print(f'Version: {wirelesssgx.__version__}')" 2>/dev/null || echo "Version: Latest"
else
    wirelesssgx --version 2>/dev/null || echo "Version: Latest"
fi

echo
echo "Run 'wirelesssgx' to start the application"