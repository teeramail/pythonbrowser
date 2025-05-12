#!/usr/bin/env python3
"""
Kiosk Browser - A full-screen browser for kiosk machines running on Windows or Linux
Features:
- Automatically loads a specified website
- Supports autoplay of sound
- Auto-print functionality
- Runs in fullscreen kiosk mode
"""

import sys
import os
import platform
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtGui import QKeySequence
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

# Import configuration
try:
    from kiosk_config import *
except ImportError:
    # Default configuration if config file is missing
    DEFAULT_URL = "https://example.com"
    AUTO_PRINT_INTERVAL = 3600000
    AUTO_PRINT_ENABLED = True
    ENABLE_AUTOPLAY = True
    KIOSK_MODE = True
    BROWSER_WIDTH = 1280
    BROWSER_HEIGHT = 800
    DEV_MODE = True
    EXIT_SHORTCUT_ENABLED = True

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

class WebEngineUrlInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts URL requests to modify headers for autoplay support"""
    def interceptRequest(self, info):
        # Add headers to enable autoplay
        info.setHttpHeader(b"Autoplay-Policy", b"no-user-gesture-required")

class KioskBrowser(QMainWindow):
    def __init__(self, url=DEFAULT_URL):
        super().__init__()
        self.init_ui()
        self.load_url(url)
        if AUTO_PRINT_ENABLED:
            self.setup_auto_print()
        
    def init_ui(self):
        # Create web view
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        
        # Configure web settings
        settings = self.web_view.settings()
        
        # Enable autoplay
        if ENABLE_AUTOPLAY:
            settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
            settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        
        # Set up kiosk mode
        if KIOSK_MODE:
            self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            self.showFullScreen()
            
            # Add escape key shortcut to exit (for development)
            if EXIT_SHORTCUT_ENABLED:
                self.exit_shortcut = QShortcut(QKeySequence("Ctrl+Alt+Q"), self)
                self.exit_shortcut.activated.connect(self.close)
        else:
            # If not in kiosk mode, set a reasonable window size
            self.resize(BROWSER_WIDTH, BROWSER_HEIGHT)
        
        self.setWindowTitle("Kiosk Browser")
        
    def load_url(self, url):
        """Load the specified URL"""
        self.web_view.load(QUrl(url))
        
    def setup_auto_print(self):
        """Set up auto-print functionality"""
        if AUTO_PRINT_INTERVAL > 0:
            self.print_timer = QTimer(self)
            self.print_timer.timeout.connect(self.print_page)
            self.print_timer.start(AUTO_PRINT_INTERVAL)
    
    def print_page(self):
        """Print the current page"""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.NativeFormat)
        
        # Use default printer without showing dialog
        self.web_view.page().print(printer, self.on_print_finished)
    
    def on_print_finished(self, success):
        """Callback for print completion"""
        print(f"Print {'succeeded' if success else 'failed'}")

def main():
    # Get URL from command line if provided
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set up request interceptor for autoplay
    interceptor = WebEngineUrlInterceptor()
    app.web_engine_url_request_interceptor = interceptor
    
    # Platform-specific adjustments
    if IS_LINUX:
        print("Running on Linux")
        # Linux-specific settings can be added here
    elif IS_WINDOWS:
        print("Running on Windows")
        # Windows-specific settings can be added here
    
    # Create and show browser
    browser = KioskBrowser(url)
    browser.show()
    
    print(f"Kiosk browser started - loading {url}")
    print(f"Press Ctrl+Alt+Q to exit" if EXIT_SHORTCUT_ENABLED else "")
    
    # Start application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
