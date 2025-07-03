# Wireless@SGx Linux TUI

A modern, user-friendly TUI (Text User Interface) application for setting up Wireless@SGx on Linux systems. No more manual configuration or command-line hassles!

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 🎨 **Beautiful TUI** - Modern terminal interface using Textual framework
- 🔐 **Secure Storage** - Credentials stored securely in system keyring
- 🔧 **Auto Configuration** - Automatically configures NetworkManager
- 🌐 **Multi-ISP Support** - Works with Singtel and Starhub
- 📱 **Easy OTP Entry** - User-friendly OTP input with timer
- 🚀 **One-Line Install** - Simple installation process

## Quick Start

### Option 1: Install from PyPI (Recommended)
```bash
pip install wirelesssgx
wirelesssgx
```

### Option 2: One-Line Installer
```bash
curl -sSL https://raw.githubusercontent.com/siva-sub/wireless-sgx-linux-tui/master/install.sh | bash
```

### Option 3: Install from Source
```bash
git clone https://github.com/siva-sub/wireless-sgx-linux-tui.git
cd wireless-sgx-linux-tui
pip install -e .
wirelesssgx
```

## Usage

1. **Launch the application**:
   ```bash
   wirelesssgx
   ```
   Or if you prefer:
   ```bash
   python -m wirelesssgx
   ```

2. **Choose your action**:
   - **New Registration**: For first-time users
   - **Retrieve Existing**: If you already have an account
   - **Auto-Connect**: If you have saved credentials

3. **Enter your details**:
   - Phone number (Singapore mobile)
   - Date of birth (DDMMYYYY format)
   - Select your ISP (Singtel/Starhub)

4. **Enter OTP**:
   - Check your SMS for the OTP
   - Enter it in the application

5. **Done!** Your credentials are saved and network is configured automatically.

## What is a TUI?

This application uses a Text User Interface (TUI) - it runs in your terminal but provides a graphical-like experience with:
- Mouse support
- Buttons and forms
- Colored interface
- Keyboard navigation

Think of it as a GUI that runs in your terminal!

## Supported ISPs

- **Singtel** - Fully tested and working
- **Starhub** - Fully tested and working

Note: M1 and SIMBA are also Wireless@SG operators but their API endpoints are not publicly available for this registration method.

## Requirements

- Python 3.8 or higher
- Linux with NetworkManager or systemd-networkd
- Active Singapore mobile number for OTP

## Troubleshooting

### Common Issues

1. **"Cannot connect to NetworkManager"**
   - Ensure NetworkManager is running: `sudo systemctl start NetworkManager`

2. **"Keyring access denied"**
   - Install gnome-keyring or similar: `sudo apt install gnome-keyring`

3. **"OTP timeout"**
   - The application will offer to resend OTP
   - Check your phone number is correct

### Manual Network Configuration

If automatic configuration fails, you can manually configure using the displayed credentials:

1. Open your network settings
2. Add new WiFi connection
3. Settings:
   - SSID: `Wireless@SGx`
   - Security: WPA & WPA2 Enterprise
   - Authentication: PEAP
   - Inner Authentication: MSCHAPv2
   - Username: [displayed username]
   - Password: [displayed password]

## Development

### Setup Development Environment
```bash
git clone https://github.com/siva-sub/wireless-sgx-linux-tui.git
cd wireless-sgx-linux-tui
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on the original [wireless-sg-wifi-for-linux](https://github.com/konaylintun09/wireless-sg-wifi-for-linux) project
- Uses the [Textual](https://github.com/textualize/textual) framework for the TUI
- Thanks to the Singapore tech community for reverse engineering efforts

## Disclaimer

This is an unofficial tool. Use at your own risk. The authors are not responsible for any misuse or damage.