#!/bin/bash

# Wireless@SGx Linux TUI Installer
# Author: Sivasubramanian Ramanathan
# Repository: https://github.com/siva-sub/wireless-sgx-linux-tui

set -e

echo "🌐 Wireless@SGx Linux TUI Installer"
echo "=================================="
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}Error: This installer is for Linux only${NC}"
    exit 1
fi

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${RED}Error: Python $python_version is installed, but version $required_version or higher is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $python_version found${NC}"

# Check for pip
echo "Checking pip..."
if ! python3 -m pip --version &> /dev/null; then
    echo -e "${YELLOW}pip not found, installing...${NC}"
    wget https://bootstrap.pypa.io/get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
fi

# Create virtual environment (optional but recommended)
echo
read -p "Do you want to install in a virtual environment? (recommended) [Y/n] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv ~/.wirelesssgx-venv
    source ~/.wirelesssgx-venv/bin/activate
    
    # Add activation to shell rc file
    shell_rc=""
    if [ -f ~/.bashrc ]; then
        shell_rc=~/.bashrc
    elif [ -f ~/.zshrc ]; then
        shell_rc=~/.zshrc
    fi
    
    if [ ! -z "$shell_rc" ]; then
        echo >> $shell_rc
        echo "# Wireless@SGx virtual environment" >> $shell_rc
        echo "alias wirelesssgx='source ~/.wirelesssgx-venv/bin/activate && wirelesssgx'" >> $shell_rc
    fi
fi

# Install from PyPI or GitHub
echo
echo "Installation method:"
echo "1) Install from PyPI (stable)"
echo "2) Install from GitHub (latest)"
read -p "Choose [1-2]: " install_method

case $install_method in
    1)
        echo "Installing from PyPI..."
        pip install wirelesssgx
        ;;
    2)
        echo "Installing from GitHub..."
        pip install git+https://github.com/siva-sub/wireless-sgx-linux-tui.git
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Check for network manager
echo
echo "Checking network configuration..."
if systemctl is-active --quiet NetworkManager; then
    echo -e "${GREEN}✓ NetworkManager detected${NC}"
elif systemctl is-active --quiet systemd-networkd; then
    echo -e "${GREEN}✓ systemd-networkd detected${NC}"
else
    echo -e "${YELLOW}⚠ No supported network manager detected${NC}"
    echo "Manual configuration may be required"
fi

# Create desktop entry
echo
read -p "Create desktop entry for application launcher? [Y/n] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    desktop_file=~/.local/share/applications/wirelesssgx.desktop
    mkdir -p ~/.local/share/applications
    
    cat > $desktop_file << EOF
[Desktop Entry]
Name=Wireless@SGx
Comment=Connect to Singapore's public WiFi
Exec=wirelesssgx
Icon=network-wireless
Terminal=true
Type=Application
Categories=Network;System;
Keywords=wifi;wireless;singapore;
EOF
    
    echo -e "${GREEN}✓ Desktop entry created${NC}"
fi

# Installation complete
echo
echo -e "${GREEN}✅ Installation complete!${NC}"
echo
echo "To run Wireless@SGx:"
echo "  wirelesssgx"
echo
echo "Or if you installed in a virtual environment:"
echo "  source ~/.wirelesssgx-venv/bin/activate"
echo "  wirelesssgx"
echo
echo "Enjoy connecting to Wireless@SGx!"