#!/usr/bin/env python3
"""
Thermal Printer Module for 58mm Xprinter
This module provides direct USB communication with the thermal printer
"""

import usb.core
import usb.util
import time
from PIL import Image, ImageOps
import os

# Import printer configuration
try:
    from printer_config import VENDOR_ID, PRODUCT_ID, THAI_ENCODING, THAI_CODEPAGE, THAI_CHAR_MODE
except ImportError:
    # Default configuration if config file is missing
    VENDOR_ID = 0x0483  # Xprinter USB Printer P
    PRODUCT_ID = 0x070b  # Xprinter USB Printer P
    THAI_ENCODING = 'utf-8'  # Use UTF-8 for Thai encoding
    THAI_CODEPAGE = 20  # Thai code page 42
    THAI_CHAR_MODE = 49  # 3-pass mode

# ESC/POS Commands
ESC = 0x1B  # Escape
GS = 0x1D   # Group Separator
FS = 0x1C   # Field Separator
INIT = [ESC, 0x40]  # Initialize printer
LINE_FEED = [0x0A]  # Line feed
CUT = [GS, 0x56, 0x00]  # Full cut
ALIGN_CENTER = [ESC, 0x61, 0x01]  # Center alignment
ALIGN_LEFT = [ESC, 0x61, 0x00]  # Left alignment
BOLD_ON = [ESC, 0x45, 0x01]  # Bold on
BOLD_OFF = [ESC, 0x45, 0x00]  # Bold off
DOUBLE_HEIGHT_ON = [ESC, 0x21, 0x10]  # Double height on
DOUBLE_HEIGHT_OFF = [ESC, 0x21, 0x00]  # Double height off
UNDERLINE_ON = [ESC, 0x2D, 0x01]  # Underline on
UNDERLINE_OFF = [ESC, 0x2D, 0x00]  # Underline off

# Character code tables
CODEPAGE_PC437 = [ESC, 0x74, 0x00]  # USA, Standard Europe
CODEPAGE_KATAKANA = [ESC, 0x74, 0x01]  # Katakana
CODEPAGE_PC850 = [ESC, 0x74, 0x02]  # Multilingual
CODEPAGE_PC860 = [ESC, 0x74, 0x03]  # Portuguese
CODEPAGE_PC863 = [ESC, 0x74, 0x04]  # Canadian-French
CODEPAGE_PC865 = [ESC, 0x74, 0x05]  # Nordic
CODEPAGE_WPC1252 = [ESC, 0x74, 0x10]  # Latin 1
CODEPAGE_PC866 = [ESC, 0x74, 0x11]  # Cyrillic #2
CODEPAGE_PC852 = [ESC, 0x74, 0x12]  # Latin 2
CODEPAGE_PC858 = [ESC, 0x74, 0x13]  # Euro
CODEPAGE_THAI42 = [ESC, 0x74, 0x14]  # Thai character code 42
CODEPAGE_THAI11 = [ESC, 0x74, 0x15]  # Thai character code 11
CODEPAGE_THAI13 = [ESC, 0x74, 0x16]  # Thai character code 13
CODEPAGE_THAI14 = [ESC, 0x74, 0x17]  # Thai character code 14
CODEPAGE_THAI16 = [ESC, 0x74, 0x18]  # Thai character code 16
CODEPAGE_THAI17 = [ESC, 0x74, 0x19]  # Thai character code 17
CODEPAGE_THAI18 = [ESC, 0x74, 0x1A]  # Thai character code 18

# Thai character mode commands
THAI_CHARACTER_MODE_3PASS = [FS, 0x45, 0x31]  # Thai character 3-pass printing mode
THAI_CHARACTER_MODE_1PASS = [FS, 0x45, 0x30]  # Thai character 1-pass printing mode

class ThermalPrinter:
    def __init__(self):
        self.dev = None
        self.ep_out = None
        self.is_connected = False
    
    def connect(self):
        """Connect to the thermal printer"""
        try:
            # Find the printer
            self.dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
            
            if self.dev is None:
                print("Printer not found! Make sure it's connected and powered on.")
                return False
            
            # Detach kernel driver if active
            if self.dev.is_kernel_driver_active(0):
                try:
                    self.dev.detach_kernel_driver(0)
                    print("Kernel driver detached successfully")
                except usb.core.USBError as e:
                    if "Permission denied" in str(e) or "Access denied" in str(e):
                        print("\nPermission denied accessing the printer. This usually means:")
                        print("1. The udev rules are not set up correctly")
                        print("2. You need to run the program with sudo privileges")
                        print("\nTry running with sudo or check if the udev rules are properly installed.")
                        return False
                    print(f"Error detaching kernel driver: {e}")
                    return False
                except Exception as e:
                    print(f"Error detaching kernel driver: {e}")
                    return False
            
            # Set configuration
            try:
                self.dev.set_configuration()
                print("USB configuration set successfully")
            except usb.core.USBError as e:
                if "Permission denied" in str(e) or "Access denied" in str(e):
                    print("\nPermission denied setting USB configuration. This usually means:")
                    print("1. The udev rules are not set up correctly")
                    print("2. You need to run the program with sudo privileges")
                    print("\nTry running with sudo or check if the udev rules are properly installed.")
                    return False
                print(f"Error setting configuration: {e}")
                return False
            except Exception as e:
                print(f"Error setting configuration: {e}")
                return False
            
            # Get endpoint
            cfg = self.dev.get_active_configuration()
            interface = cfg[(0,0)]
            
            self.ep_out = usb.util.find_descriptor(
                interface,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )
            
            if self.ep_out is None:
                print("Output endpoint not found!")
                return False
            
            # Initialize printer
            self.ep_out.write(bytes(INIT))
            self.is_connected = True
            print("Successfully connected to thermal printer")
            return True
            
        except usb.core.USBError as e:
            if "Permission denied" in str(e) or "Access denied" in str(e):
                print("\nPermission denied accessing the printer. This usually means:")
                print("1. The udev rules are not set up correctly")
                print("2. You need to run the program with sudo privileges")
                print("\nTry running with sudo or check if the udev rules are properly installed.")
            else:
                print(f"USB error connecting to printer: {e}")
            return False
        except Exception as e:
            print(f"Error connecting to printer: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def disconnect(self):
        """Disconnect from the printer"""
        if self.dev:
            usb.util.dispose_resources(self.dev)
            self.is_connected = False
    
    def print_text(self, text):
        """Print text to the thermal printer"""
        if not self.is_connected:
            if not self.connect():
                return False
        
        try:
            # Initialize printer
            self.ep_out.write(bytes(INIT))
            
            # Try Thai character mode for better Thai support
            # Enable Thai 3-pass mode for better quality
            self.ep_out.write(bytes(THAI_CHARACTER_MODE_3PASS))
            
            # Set Thai character code table
            self.ep_out.write(bytes(CODEPAGE_THAI42))
            
            # Encode text using the configured encoding
            try:
                print(f"Using {THAI_ENCODING} encoding")
                encoded_text = text.encode(THAI_ENCODING, errors='replace')
                self.ep_out.write(encoded_text)
            except LookupError:
                # If the configured encoding is not available, fall back to UTF-8
                print(f"{THAI_ENCODING} encoding not available, falling back to UTF-8")
                encoded_text = text.encode('utf-8', errors='replace')
                self.ep_out.write(encoded_text)
            
            self.ep_out.write(bytes(LINE_FEED))
            return True
        except Exception as e:
            print(f"Error printing text: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def feed_paper(self, lines=1):
        """Feed paper by specified number of lines (default: 1)
        This method provides controlled paper feeding"""
        if not self.is_connected:
            if not self.connect():
                return False
        
        try:
            # Feed only the specified number of lines
            for _ in range(min(lines, 10)):  # Limit to max 10 lines for safety
                self.ep_out.write(bytes(LINE_FEED))
            return True
        except Exception as e:
            print(f"Error feeding paper: {e}")
            return False
    
    def print_receipt(self, title, content, footer=None, max_length=500):
        """Print a formatted receipt with controlled paper usage
        max_length: Maximum content length to prevent excessive paper feed"""
        if not self.is_connected:
            if not self.connect():
                return False
        
        try:
            # Initialize printer
            self.ep_out.write(bytes(INIT))
            
            # Set Thai character mode (3-pass or 1-pass)
            if THAI_CHAR_MODE == 49:  # 3-pass mode
                self.ep_out.write(bytes(THAI_CHARACTER_MODE_3PASS))
            else:  # 1-pass mode
                self.ep_out.write(bytes(THAI_CHARACTER_MODE_1PASS))
            
            # Set Thai character code table
            self.ep_out.write(bytes(CODEPAGE_THAI42))
            
            # Encoding function to handle Thai text
            def encode_thai(text):
                try:
                    # Always use UTF-8 for Thai text
                    return text.encode('utf-8', errors='replace')
                except Exception as e:
                    print(f"Error encoding Thai text: {e}")
                    # Fall back to basic encoding if UTF-8 fails
                    return text.encode('ascii', errors='replace')
            
            # Limit content length to prevent excessive paper feed
            if content and len(content) > max_length:
                content = content[:max_length] + "\n[Content truncated to save paper]\n"
            
            # Center and bold the title
            self.ep_out.write(bytes(ALIGN_CENTER))
            self.ep_out.write(bytes(BOLD_ON))
            self.ep_out.write(bytes(DOUBLE_HEIGHT_ON))
            self.ep_out.write(encode_thai(title))
            self.ep_out.write(bytes(LINE_FEED))
            self.ep_out.write(bytes(DOUBLE_HEIGHT_OFF))
            self.ep_out.write(bytes(BOLD_OFF))
            self.ep_out.write(bytes(LINE_FEED))
            
            # Print content with left alignment
            self.ep_out.write(bytes(ALIGN_LEFT))
            self.ep_out.write(encode_thai(content))
            self.ep_out.write(bytes(LINE_FEED))
            
            # Print footer if provided
            if footer:
                self.ep_out.write(bytes(ALIGN_CENTER))
                self.ep_out.write(encode_thai(footer))
                self.ep_out.write(bytes(LINE_FEED))
            
            # Feed paper (limited) and cut
            self.feed_paper(2)  # Feed only 2 lines before cutting
            self.ep_out.write(bytes(CUT))
            
            return True
        except Exception as e:
            print(f"Error printing receipt: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cut_paper(self):
        """Cut the paper"""
        if not self.is_connected:
            if not self.connect():
                return False
        
        try:
            self.ep_out.write(bytes(CUT))
            return True
        except Exception as e:
            print(f"Error cutting paper: {e}")
            return False
            
    def print_image(self, image_path):
        """Print a PNG image using ESC/POS raster graphics"""
        if not self.is_connected:
            if not self.connect():
                return False
        try:
            # Open and process image
            img = Image.open(image_path)
            # Make sure black text on white background is preserved
            img = img.convert('L')  # Convert to grayscale first
            # Then threshold to pure black/white with control over threshold value
            # Lower threshold = darker output (more black)
            threshold = 200
            img = img.point(lambda p: 255 if p > threshold else 0)
            img = img.convert('1')  # Convert to 1-bit black and white
            
            # IMPORTANT: Invert the image for thermal printing
            # In thermal printing, 1 = white (no heat), 0 = black (apply heat)
            # We need to invert so black text appears black on paper
            img = ImageOps.invert(img)
            width, height = img.size
            
            # Width must be divisible by 8 for ESC/POS raster format
            if width % 8 != 0:
                # Pad the width to make it divisible by 8
                new_width = (width // 8 + 1) * 8
                new_img = Image.new('1', (new_width, height), 1)  # White background (1 = white in mode '1')
                new_img.paste(img, (0, 0))
                img = new_img
                width = new_width
            
            # ESC/POS raster bit image command
            # GS v 0 - Print raster bit image
            # Parameters: 0, width/8 (bytes per line), height low byte, height high byte
            self.ep_out.write(bytes([GS, 0x76, 0x30, 0x00, width // 8, 0x00, height & 0xFF, (height >> 8) & 0xFF]))
            
            # Send the actual image data
            pixels = img.tobytes()
            self.ep_out.write(pixels)
            
            # Feed a bit of paper and cut
            self.feed_paper(3)
            self.cut_paper()
            print(f"Image printed successfully: {image_path}")
            return True
        except Exception as e:
            print(f"Error printing image: {e}")
            import traceback
            traceback.print_exc()
            return False


# Singleton instance
_printer = None

def get_printer():
    """Get the singleton printer instance"""
    global _printer
    if _printer is None:
        _printer = ThermalPrinter()
    return _printer


# Simple test function
def test_printer():
    """Test the printer with a simple receipt"""
    try:
        print("Starting printer test...")
        printer = get_printer()
        print("Attempting to connect to printer...")
        if printer.connect():
            print("Connected to printer, sending test receipt...")
            success = printer.print_receipt(
                "TEST RECEIPT",
                "Item 1........................$10.00\n"
                "Item 2........................$15.00\n"
                "Item 3........................$20.00\n"
                "---------------------------------\n"
                "Total.........................$45.00",
                "Thank you for your purchase!\nwww.example.com"
            )
            printer.disconnect()
            if success:
                print("Test receipt printed successfully!")
                return True
            else:
                print("Failed to print test receipt.")
                return False
        else:
            print("Failed to connect to printer.")
            return False
    except Exception as e:
        print(f"Error in test_printer: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run a test print if this module is executed directly
    if test_printer():
        print("Test receipt printed successfully!")
    else:
        print("Failed to print test receipt.")
