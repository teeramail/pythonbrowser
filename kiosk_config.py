"""
Configuration file for the kiosk browser
Edit this file to customize your kiosk browser settings
"""

# Target website to load
DEFAULT_URL = "https://teachersco.vercel.app/about"  # Change this to your target website

# Auto print settings
AUTO_PRINT_INTERVAL = 0  # Set to 0 to disable auto-printing
AUTO_PRINT_ENABLED = True  # Only print once when page loads

# Browser settings
ENABLE_AUTOPLAY = True
KIOSK_MODE = True
BROWSER_WIDTH = 1280
BROWSER_HEIGHT = 800

# Development settings
DEV_MODE = True  # Set to False in production
EXIT_SHORTCUT_ENABLED = True  # Set to False in production
