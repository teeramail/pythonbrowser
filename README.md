# Kiosk Browser for Ubuntu

A full-screen kiosk browser built with Python and PyQt5, designed for Ubuntu kiosk machines.

## Features

- **Fullscreen Kiosk Mode**: Runs in frameless fullscreen mode
- **Autoplay Support**: Enables autoplay of audio and video content
- **Auto-Print Functionality**: Automatically prints the page at configurable intervals
- **Single Website Focus**: Loads a specific website on startup
- **Ubuntu Integration**: Can be configured to start automatically when Ubuntu boots

## Installation

### 1. Install Dependencies

```bash
# Install Python and pip if not already installed
sudo apt update
sudo apt install -y python3 python3-pip xorg

# Install required Python packages
pip3 install -r requirements.txt

# Install Qt dependencies
sudo apt install -y libqt5webkit5-dev libqt5webengine5 libqt5webenginewidgets5
```

### 2. Configure the Browser

Edit `kiosk_browser.py` to set your desired configuration:

```python
# Configuration
DEFAULT_URL = "https://example.com"  # Change this to your target website
AUTO_PRINT_INTERVAL = 3600000  # Auto print every hour (in ms), set to 0 to disable
ENABLE_AUTOPLAY = True
KIOSK_MODE = True
```

### 3. Make Scripts Executable

```bash
chmod +x kiosk_browser.py
chmod +x start_kiosk.sh
```

## Setting Up Auto-Start on Ubuntu

### Method 1: Using Autostart

1. Create a desktop entry file:

```bash
sudo nano /etc/xdg/autostart/kiosk-browser.desktop
```

2. Add the following content:

```
[Desktop Entry]
Type=Application
Name=Kiosk Browser
Exec=/full/path/to/start_kiosk.sh
Terminal=false
X-GNOME-Autostart-enabled=true
```

3. Save and exit (Ctrl+X, then Y, then Enter)

### Method 2: Using Systemd

1. Create a systemd user service:

```bash
mkdir -p ~/.config/systemd/user/
nano ~/.config/systemd/user/kiosk-browser.service
```

2. Add the following content:

```
[Unit]
Description=Kiosk Browser Service
After=graphical-session.target

[Service]
ExecStart=/full/path/to/start_kiosk.sh
Restart=on-failure

[Install]
WantedBy=graphical-session.target
```

3. Enable the service:

```bash
systemctl --user enable kiosk-browser.service
systemctl --user start kiosk-browser.service
```

## Usage

### Running Manually

```bash
./start_kiosk.sh
```

Or specify a different URL:

```bash
python3 kiosk_browser.py "https://your-website.com"
```

### Exiting the Browser

Press `Ctrl+Alt+Q` to exit the browser (this can be disabled in production by removing the shortcut in the code).

## Troubleshooting

### Printer Issues

Make sure your default printer is properly configured in Ubuntu:

```bash
sudo apt install -y cups
sudo systemctl enable cups
sudo systemctl start cups
```

Configure your printer through the CUPS web interface at http://localhost:631

### Autoplay Not Working

Some websites may still block autoplay despite the browser settings. In such cases:

1. Check if the website has specific autoplay restrictions
2. Try adding additional headers in the `WebEngineUrlInterceptor` class
3. Consider using a website that you control and can configure for kiosk use

### Display Issues

If the kiosk doesn't start properly:

```bash
# Make sure X server is running
sudo systemctl status display-manager

# Check for errors in the X log
cat /var/log/Xorg.0.log | grep EE
```

## Customization

The browser can be further customized by modifying the `kiosk_browser.py` file:

- Change the auto-print interval
- Modify web engine settings
- Add custom keyboard shortcuts
- Implement additional features like auto-refresh
