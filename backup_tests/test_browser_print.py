#!/usr/bin/env python3
"""
Test script to launch the kiosk browser and trigger a print operation
Optimized for 58mm thermal receipt printer with Thai character support
"""

import sys
import time
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from kiosk_browser import KioskBrowser

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Use the UTF-8 Thai test page
    thermal_test_page = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thai_utf8_test.html')
    
    # Convert to file URL
    file_url = QUrl.fromLocalFile(thermal_test_page).toString()
    
    # Create and show browser
    browser = KioskBrowser(file_url)
    browser.show()
    
    print("Test browser started - will automatically print Thai test receipt")
    print("The page is optimized for a 58mm thermal printer with 5cm length")
    
    # Start application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
