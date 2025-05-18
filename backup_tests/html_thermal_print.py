#!/usr/bin/env python3
"""
HTML Thermal Printer - Directly prints HTML content to a 58mm thermal printer
"""

import sys
import os
import argparse
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl, QSize, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtGui import QPainter
from PyQt5.QtPrintSupport import QPrinter
from thermal_printer import ThermalPrinter

class HtmlPrinter:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.view = QWebEngineView()
        self.page = self.view.page()
        
        # Set page size to 58mm width (about 219 pixels at 96 DPI)
        self.page.setViewportSize(QSize(219, 800))
        
        # Connect to loadFinished signal
        self.view.loadFinished.connect(self.on_load_finished)
        self.html_loaded = False
        
    def load_html(self, html_content=None, html_file=None):
        """Load HTML content or file"""
        if html_file:
            if os.path.exists(html_file):
                self.view.load(QUrl.fromLocalFile(os.path.abspath(html_file)))
                return True
            else:
                print(f"Error: HTML file not found: {html_file}")
                return False
        elif html_content:
            self.page.setHtml(html_content)
            return True
        return False
    
    def on_load_finished(self, success):
        """Called when the HTML content is loaded"""
        if success:
            self.html_loaded = True
            print("HTML content loaded successfully")
        else:
            print("Failed to load HTML content")
    
    def print_to_thermal(self):
        """Print the loaded HTML content to the thermal printer"""
        if not self.html_loaded:
            print("No HTML content loaded")
            return False
        
        # Get the HTML content as plain text
        self.page.toPlainText(self.print_text_content)
        
        # Wait for the application to process events
        self.app.processEvents()
        
        return True
    
    def print_text_content(self, text):
        """Print the extracted text content to the thermal printer"""
        if not text:
            print("No text content to print")
            return
        
        print(f"Printing content ({len(text)} characters)...")
        
        try:
            # Connect to the thermal printer
            printer = ThermalPrinter()
            
            # Print the content as a receipt
            title = "Receipt"
            footer = "Thank you!"
            
            # Extract title from the text if possible
            lines = text.split('\n')
            if lines and lines[0].strip():
                title = lines[0].strip()
                content = '\n'.join(lines[1:])
            else:
                content = text
            
            # Print the receipt
            printer.print_receipt(title, content, footer)
            print("Content printed successfully to thermal printer")
            
        except Exception as e:
            print(f"Error printing to thermal printer: {e}")
    
    def render_to_image(self, output_file):
        """Render the HTML content to an image file"""
        if not self.html_loaded:
            print("No HTML content loaded")
            return False
        
        # Create a printer object
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(output_file)
        printer.setPageSize(QPrinter.Custom)
        printer.setPageSizeMM(QSize(58, 50))  # 58mm x 50mm
        printer.setFullPage(True)
        
        # Create a painter to paint the web content onto the printer
        painter = QPainter()
        if painter.begin(printer):
            self.page.render(painter)
            painter.end()
            print(f"HTML content rendered to {output_file}")
            return True
        else:
            print("Failed to start painting")
            return False
    
    def run(self):
        """Run the application event loop"""
        return self.app.exec_()

def main():
    parser = argparse.ArgumentParser(description='Print HTML content to a 58mm thermal printer')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', help='HTML file to print')
    group.add_argument('--content', help='HTML content to print')
    parser.add_argument('--image', help='Save as image instead of printing')
    args = parser.parse_args()
    
    printer = HtmlPrinter()
    
    if args.file:
        if not printer.load_html(html_file=args.file):
            return 1
    elif args.content:
        if not printer.load_html(html_content=args.content):
            return 1
    
    # Wait a bit for the content to load
    import time
    time.sleep(1)
    
    if args.image:
        printer.render_to_image(args.image)
    else:
        printer.print_to_thermal()
    
    # Run the application event loop
    return printer.run()

if __name__ == "__main__":
    sys.exit(main())
