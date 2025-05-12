#!/bin/bash
# Startup script for kiosk browser

# Wait for the desktop environment to fully load (adjust time as needed)
sleep 10

# Navigate to the directory containing the kiosk browser
cd "$(dirname "$0")"

# Launch the kiosk browser with the target URL
# Replace the URL with your desired website
python3 kiosk_browser.py "https://example.com"
