#!/bin/bash

# Wireless@SGx Linux TUI Uninstaller
# Author: Sivasubramanian Ramanathan
# Repository: https://github.com/siva-sub/wireless-sgx-linux-tui

set -e

echo "🗑️  Wireless@SGx Linux TUI Uninstaller"
echo "===================================="
echo

# Colors
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
NC=$'\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}Error: This uninstaller is for Linux only${NC}"
    exit 1
fi

# Confirmation
echo -e "${YELLOW}This will remove Wireless@SGx and all its components.${NC}"
read -p "Are you sure you want to continue? [y/N] " -n 1 -r < /dev/tty
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo
echo "Removing Wireless@SGx components..."

# Remove from virtual environment if exists
if [ -d ~/.wirelesssgx-venv ]; then
    echo "Removing virtual environment..."
    rm -rf ~/.wirelesssgx-venv
    echo -e "${GREEN}✓ Virtual environment removed${NC}"
    
    # Remove alias from shell rc files
    for rc_file in ~/.bashrc ~/.zshrc; do
        if [ -f "$rc_file" ]; then
            # Remove the lines related to wirelesssgx
            sed -i '/# Wireless@SGx virtual environment/d' "$rc_file"
            sed -i '/alias wirelesssgx=/d' "$rc_file"
        fi
    done
    echo -e "${GREEN}✓ Shell aliases removed${NC}"
else
    # Try to uninstall from system
    echo "Attempting to uninstall from system..."
    pip uninstall -y wirelesssgx 2>/dev/null || true
    pip3 uninstall -y wirelesssgx 2>/dev/null || true
fi

# Remove desktop entry
if [ -f ~/.local/share/applications/wirelesssgx.desktop ]; then
    rm ~/.local/share/applications/wirelesssgx.desktop
    echo -e "${GREEN}✓ Desktop entry removed${NC}"
fi

# Remove launcher wrapper
if [ -f ~/.local/bin/wirelesssgx-launcher ]; then
    rm ~/.local/bin/wirelesssgx-launcher
    echo -e "${GREEN}✓ Launcher wrapper removed${NC}"
fi

# Remove saved credentials (optional)
echo
read -p "Remove saved credentials? [y/N] " -n 1 -r < /dev/tty
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Try to remove from various keyring backends
    python3 -c "
import keyring
try:
    keyring.delete_password('wirelesssgx', 'credentials')
    print('✓ Saved credentials removed')
except:
    pass
" 2>/dev/null || echo "No saved credentials found"
fi

# Remove network configurations (optional)
echo
read -p "Remove network configurations? [y/N] " -n 1 -r < /dev/tty
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # NetworkManager
    if command -v nmcli &> /dev/null; then
        nmcli connection delete "Wireless@SGx" 2>/dev/null && \
            echo -e "${GREEN}✓ NetworkManager configuration removed${NC}" || \
            echo "No NetworkManager configuration found"
    fi
    
    # systemd-networkd
    if [ -f /etc/systemd/network/99-wirelesssgx.network ]; then
        sudo rm /etc/systemd/network/99-wirelesssgx.network
        sudo rm -f /etc/wpa_supplicant/wpa_supplicant-wirelesssgx.conf
        sudo systemctl restart systemd-networkd
        echo -e "${GREEN}✓ systemd-networkd configuration removed${NC}"
    fi
fi

echo
echo -e "${GREEN}✅ Wireless@SGx has been uninstalled!${NC}"
echo
echo "Thank you for using Wireless@SGx Linux TUI."
echo "If you have any feedback, please visit:"
echo "https://github.com/siva-sub/wireless-sgx-linux-tui/issues"