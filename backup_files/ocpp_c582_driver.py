#!/usr/bin/env python3
"""
OCPP-C582 Thermal Receipt Printer Driver for Ubuntu
Specifically designed for the OCPP-C582 58mm thermal printer
"""

import sys
import usb.core
import usb.util
import time
import argparse

# OCPP-C582 Printer constants
VENDOR_ID = 0x0483  # STMicroelectronics
PRODUCT_ID = 0x070b  # USB Printer P

# ESC/POS Commands
ESC = 0x1B  # Escape
GS = 0x1D   # Group Separator
FS = 0x1C   # Field Separator
LF = 0x0A   # Line Feed (new line)

# Thai code page (CP874)
THAI_CODEPAGE = [ESC, 0x74, 0x15]  # Thai character code page

# Initialize printer
INIT = [ESC, 0x40]

# Text formatting
CENTER = [ESC, 0x61, 0x01]  # Center alignment
LEFT = [ESC, 0x61, 0x00]    # Left alignment
RIGHT = [ESC, 0x61, 0x02]   # Right alignment
BOLD_ON = [ESC, 0x45, 0x01]  # Bold on
BOLD_OFF = [ESC, 0x45, 0x00]  # Bold off
DOUBLE_HEIGHT_ON = [ESC, 0x21, 0x10]  # Double height on
DOUBLE_HEIGHT_OFF = [ESC, 0x21, 0x00]  # Double height off
UNDERLINE_ON = [ESC, 0x2D, 0x01]  # Underline on
UNDERLINE_OFF = [ESC, 0x2D, 0x00]  # Underline off

# Paper cut
PARTIAL_CUT = [GS, 0x56, 0x01]  # Partial cut
FULL_CUT = [GS, 0x56, 0x00]     # Full cut

# Line spacing
DEFAULT_LINE_SPACING = [ESC, 0x32]  # Default line spacing
SET_LINE_SPACING = [ESC, 0x33]      # Set line spacing

# Character size
NORMAL_SIZE = [GS, 0x21, 0x00]  # Normal size
DOUBLE_WIDTH = [GS, 0x21, 0x10]  # Double width
DOUBLE_HEIGHT = [GS, 0x21, 0x01]  # Double height
QUAD_SIZE = [GS, 0x21, 0x11]  # Quad size

# Barcode
BARCODE_HEIGHT = [GS, 0x68, 0x50]  # Barcode height
BARCODE_WIDTH = [GS, 0x77, 0x02]   # Barcode width
BARCODE_POSITION = [GS, 0x48, 0x02]  # Barcode position

# QR Code
QR_SIZE = [GS, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x43, 0x05]  # QR size
QR_ERROR = [GS, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x45, 0x31]  # QR error correction

class OCPPC582Printer:
    """OCPP-C582 Thermal Receipt Printer Driver"""
    
    def __init__(self):
        """Initialize the printer connection"""
        self.ep_out = None
        self.printer = None
    
    def connect(self):
        """Connect to the OCPP-C582 printer"""
        try:
            # Find the printer
            self.printer = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
            
            if self.printer is None:
                print("Printer not found! Make sure it's connected and powered on.")
                return False
            
            # Detach kernel driver if active
            if self.printer.is_kernel_driver_active(0):
                try:
                    self.printer.detach_kernel_driver(0)
                    print("Kernel driver detached")
                except Exception as e:
                    print(f"Error detaching kernel driver: {e}")
                    return False
            
            # Set configuration
            try:
                self.printer.set_configuration()
                print("USB configuration set")
            except Exception as e:
                print(f"Error setting configuration: {e}")
                return False
            
            # Get endpoint
            cfg = self.printer.get_active_configuration()
            intf = cfg[(0,0)]
            
            self.ep_out = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: 
                    usb.util.endpoint_direction(e.bEndpointAddress) == 
                    usb.util.ENDPOINT_OUT
            )
            
            if self.ep_out is None:
                print("Could not find endpoint")
                return False
            
            # Initialize printer
            self.ep_out.write(bytes(INIT))
            
            # Set Thai code page
            self.ep_out.write(bytes(THAI_CODEPAGE))
            
            print("Successfully connected to OCPP-C582 printer")
            return True
            
        except Exception as e:
            print(f"Error connecting to printer: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the printer"""
        if self.printer:
            usb.util.dispose_resources(self.printer)
            print("Printer disconnected")
    
    def write(self, data):
        """Write raw data to the printer"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            self.ep_out.write(data)
            return True
        except Exception as e:
            print(f"Error writing to printer: {e}")
            return False
    
    def print_text(self, text, encoding='utf-8'):
        """Print text with the specified encoding"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            self.ep_out.write(text.encode(encoding, errors='replace'))
            self.ep_out.write(bytes([LF]))
            return True
        except Exception as e:
            print(f"Error printing text: {e}")
            return False
    
    def set_alignment(self, alignment):
        """Set text alignment (CENTER, LEFT, RIGHT)"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            self.ep_out.write(bytes(alignment))
            return True
        except Exception as e:
            print(f"Error setting alignment: {e}")
            return False
    
    def set_bold(self, bold=True):
        """Set bold text"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            if bold:
                self.ep_out.write(bytes(BOLD_ON))
            else:
                self.ep_out.write(bytes(BOLD_OFF))
            return True
        except Exception as e:
            print(f"Error setting bold: {e}")
            return False
    
    def set_double_height(self, double=True):
        """Set double height text"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            if double:
                self.ep_out.write(bytes(DOUBLE_HEIGHT_ON))
            else:
                self.ep_out.write(bytes(DOUBLE_HEIGHT_OFF))
            return True
        except Exception as e:
            print(f"Error setting double height: {e}")
            return False
    
    def set_underline(self, underline=True):
        """Set underlined text"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            if underline:
                self.ep_out.write(bytes(UNDERLINE_ON))
            else:
                self.ep_out.write(bytes(UNDERLINE_OFF))
            return True
        except Exception as e:
            print(f"Error setting underline: {e}")
            return False
    
    def feed(self, lines=1):
        """Feed paper by the specified number of lines"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            for _ in range(lines):
                self.ep_out.write(bytes([LF]))
            return True
        except Exception as e:
            print(f"Error feeding paper: {e}")
            return False
    
    def cut(self, partial=False):
        """Cut the paper (full or partial cut)"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            if partial:
                self.ep_out.write(bytes(PARTIAL_CUT))
            else:
                self.ep_out.write(bytes(FULL_CUT))
            return True
        except Exception as e:
            print(f"Error cutting paper: {e}")
            return False
    
    def print_receipt(self, title, items, total, footer=None):
        """Print a formatted receipt"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            # Print header
            self.set_alignment(CENTER)
            self.set_bold(True)
            self.set_double_height(True)
            self.print_text(title)
            self.set_double_height(False)
            self.set_bold(False)
            self.feed(1)
            
            # Print date and time
            self.set_alignment(LEFT)
            from datetime import datetime
            now = datetime.now()
            date_str = now.strftime("%d/%m/%Y")
            time_str = now.strftime("%H:%M:%S")
            self.print_text(f"Date: {date_str}")
            self.print_text(f"Time: {time_str}")
            self.feed(1)
            
            # Print items
            for item in items:
                name = item.get('name', '')
                price = item.get('price', 0)
                qty = item.get('qty', 1)
                
                self.print_text(f"{name} x{qty}")
                self.set_alignment(RIGHT)
                self.print_text(f"{price:.2f}")
                self.set_alignment(LEFT)
            
            self.feed(1)
            
            # Print total
            self.set_alignment(LEFT)
            self.set_bold(True)
            self.print_text("Total:")
            self.set_alignment(RIGHT)
            self.print_text(f"{total:.2f}")
            self.set_bold(False)
            
            # Print footer
            if footer:
                self.feed(1)
                self.set_alignment(CENTER)
                self.print_text(footer)
            
            # Feed and cut
            self.feed(3)
            self.cut()
            
            return True
        except Exception as e:
            print(f"Error printing receipt: {e}")
            return False

def test_printer():
    """Test the OCPP-C582 printer"""
    printer = OCPPC582Printer()
    
    if not printer.connect():
        print("Failed to connect to printer")
        return False
    
    try:
        # Print a test receipt
        print("Printing test receipt...")
        
        # Test receipt data
        title = "OCPP-C582 Test"
        items = [
            {'name': 'Coffee', 'price': 45.00, 'qty': 1},
            {'name': 'Tea', 'price': 35.00, 'qty': 2},
            {'name': 'Cake', 'price': 60.00, 'qty': 1}
        ]
        total = sum(item['price'] * item['qty'] for item in items)
        footer = "Thank you for your purchase!"
        
        # Print the receipt
        printer.print_receipt(title, items, total, footer)
        
        # Test Thai text
        print("Testing Thai text...")
        printer.set_alignment(CENTER)
        printer.set_bold(True)
        printer.print_text("ทดสอบภาษาไทย")
        printer.set_bold(False)
        printer.set_alignment(LEFT)
        printer.print_text("สวัสดีครับ/ค่ะ")
        printer.print_text("ขอบคุณที่ใช้บริการ")
        printer.feed(3)
        printer.cut()
        
        print("Test completed successfully")
        return True
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    
    finally:
        printer.disconnect()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='OCPP-C582 Thermal Receipt Printer Driver')
    parser.add_argument('--test', action='store_true', help='Test the printer')
    parser.add_argument('--text', type=str, help='Print text')
    parser.add_argument('--thai', action='store_true', help='Print Thai test')
    
    args = parser.parse_args()
    
    if args.test:
        test_printer()
    elif args.text:
        printer = OCPPC582Printer()
        if printer.connect():
            printer.print_text(args.text)
            printer.feed(3)
            printer.cut()
            printer.disconnect()
    elif args.thai:
        printer = OCPPC582Printer()
        if printer.connect():
            printer.print_text("ทดสอบภาษาไทย")
            printer.print_text("สวัสดีครับ/ค่ะ")
            printer.print_text("ขอบคุณที่ใช้บริการ")
            printer.feed(3)
            printer.cut()
            printer.disconnect()
    else:
        print("No action specified. Use --test, --text, or --thai")

if __name__ == "__main__":
    main()
