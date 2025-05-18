#!/usr/bin/env python3
"""
Thai Image Printer - Converts Thai text to images and prints them to the OCPP-C582 thermal printer
"""

import sys
import os
import usb.core
import usb.util
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap
import argparse

# OCPP-C582 Printer constants
VENDOR_ID = 0x0483  # STMicroelectronics
PRODUCT_ID = 0x070b  # USB Printer P

# ESC/POS Commands
ESC = 0x1B  # Escape
GS = 0x1D   # Group Separator
FS = 0x1C   # Field Separator
LF = 0x0A   # Line Feed (new line)

# Initialize printer
INIT = [ESC, 0x40]

# Text formatting
CENTER = [ESC, 0x61, 0x01]  # Center alignment
LEFT = [ESC, 0x61, 0x00]    # Left alignment
RIGHT = [ESC, 0x61, 0x02]   # Right alignment

# Paper cut
FULL_CUT = [GS, 0x56, 0x00]  # Full cut

# Image printing
SELECT_BIT_IMAGE_MODE = [ESC, 0x2A, 33]

class ThaiImagePrinter:
    """Thai Image Printer for OCPP-C582 thermal printer"""
    
    def __init__(self):
        """Initialize the printer connection"""
        self.ep_out = None
        self.printer = None
        self.width = 384  # 58mm printer width (8 dots per mm * 48mm printable area)
        
        # Default font settings - use system Thai font
        self.font_path = "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf"
        if not os.path.exists(self.font_path):
            # If Thai font not found, use another Thai font
            self.font_path = "/usr/share/fonts/truetype/noto/NotoSerifThai-Regular.ttf"
            if not os.path.exists(self.font_path):
                # Fallback to DejaVu Sans
                self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        print(f"Using font: {self.font_path}")
    

    
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
    
    def cut(self):
        """Cut the paper"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            self.ep_out.write(bytes(FULL_CUT))
            return True
        except Exception as e:
            print(f"Error cutting paper: {e}")
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
    
    def text_to_image(self, text, font_size=24, padding=10):
        """Convert text to an image"""
        try:
            # Load font
            font = ImageFont.truetype(self.font_path, font_size)
            
            # Wrap text to fit printer width
            wrapped_text = []
            for line in text.split('\n'):
                if line.strip():
                    wrapped_lines = textwrap.wrap(line, width=30)  # Adjust width as needed
                    wrapped_text.extend(wrapped_lines)
                else:
                    wrapped_text.append('')
            
            # Calculate image dimensions
            line_height = font_size + 4
            img_height = (len(wrapped_text) * line_height) + (padding * 2)
            
            # Create image with white background
            img = Image.new('L', (self.width, img_height), 255)
            draw = ImageDraw.Draw(img)
            
            # Draw text
            y = padding
            for line in wrapped_text:
                draw.text((padding, y), line, font=font, fill=0)
                y += line_height
            
            return img
        
        except Exception as e:
            print(f"Error creating image from text: {e}")
            return None
    
    def print_image(self, img):
        """Print an image to the thermal printer"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            # Ensure image is in 1-bit mode
            if img.mode != '1':
                img = img.convert('1')
            
            # Resize image to fit printer width if needed
            if img.width != self.width:
                ratio = self.width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((self.width, new_height), Image.LANCZOS)
            
            # Get image data
            pixels = list(img.getdata())
            
            # Print image in chunks
            width_bytes = (self.width + 7) // 8
            
            for y in range(0, img.height, 24):
                # Print up to 24 lines at a time
                chunk_height = min(24, img.height - y)
                
                # ESC * 33 (width_low) (width_high) (image_data)
                self.ep_out.write(bytes([ESC, 0x2A, 33, width_bytes & 0xFF, (width_bytes >> 8) & 0xFF]))
                
                # Generate and send image data
                for x in range(width_bytes):
                    for k in range(3):  # 3 bytes per column (24 dots)
                        byte = 0
                        
                        for b in range(8):
                            if y + (k * 8) + b < img.height:
                                pixel_x = x * 8 + (7 - b)
                                if pixel_x < img.width:
                                    if pixels[y * img.width + (k * 8 * img.width) + pixel_x] == 0:
                                        byte |= 1 << b
                        
                        self.ep_out.write(bytes([byte]))
                
                # Send line feed
                self.ep_out.write(bytes([LF]))
            
            return True
        
        except Exception as e:
            print(f"Error printing image: {e}")
            return False
    
    def print_thai_text(self, text, font_size=24):
        """Convert Thai text to image and print it"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            # Convert text to image
            img = self.text_to_image(text, font_size)
            if img is None:
                return False
            
            # Print the image
            return self.print_image(img)
        
        except Exception as e:
            print(f"Error printing Thai text: {e}")
            return False
    
    def print_receipt(self, title, items, total, footer=None):
        """Print a formatted receipt with Thai text support"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            # Build receipt text
            receipt_text = title + "\n\n"
            
            # Add date and time
            from datetime import datetime
            now = datetime.now()
            date_str = now.strftime("%d/%m/%Y")
            time_str = now.strftime("%H:%M:%S")
            receipt_text += f"วันที่: {date_str}\n"
            receipt_text += f"เวลา: {time_str}\n\n"
            
            # Add items
            for item in items:
                name = item.get('name', '')
                price = item.get('price', 0)
                qty = item.get('qty', 1)
                
                receipt_text += f"{name} x{qty}\n"
                receipt_text += f"{price:.2f}\n"
            
            receipt_text += "\n"
            
            # Add total
            receipt_text += f"รวม: {total:.2f}\n\n"
            
            # Add footer
            if footer:
                receipt_text += footer
            
            # Convert to image and print
            return self.print_thai_text(receipt_text)
        
        except Exception as e:
            print(f"Error printing receipt: {e}")
            return False

def test_printer():
    """Test the Thai image printer"""
    printer = ThaiImagePrinter()
    
    if not printer.connect():
        print("Failed to connect to printer")
        return False
    
    try:
        # Test Thai text
        print("Testing Thai text as image...")
        
        thai_text = """
        ทดสอบภาษาไทย
        
        สวัสดีครับ/ค่ะ
        
        ขอบคุณที่ใช้บริการ
        
        นี่คือการทดสอบการพิมพ์ภาษาไทย
        โดยการแปลงข้อความเป็นรูปภาพ
        แล้วส่งไปยังเครื่องพิมพ์ความร้อน
        """
        
        printer.set_alignment(CENTER)
        printer.print_thai_text(thai_text)
        printer.feed(1)
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
    parser = argparse.ArgumentParser(description='Thai Image Printer for OCPP-C582')
    parser.add_argument('--test', action='store_true', help='Test the printer')
    parser.add_argument('--text', type=str, help='Print Thai text')
    
    args = parser.parse_args()
    
    if args.test:
        test_printer()
    elif args.text:
        printer = ThaiImagePrinter()
        if printer.connect():
            printer.print_thai_text(args.text)
            printer.feed(1)
            printer.cut()
            printer.disconnect()
    else:
        print("No action specified. Use --test or --text")

if __name__ == "__main__":
    main()
