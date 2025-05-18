#!/usr/bin/env python3
"""
Thai Multi-Size Print - Prints Thai text with multiple font sizes as an image
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

class ThaiMultiSizePrinter:
    """Thai Multi-Size Printer for OCPP-C582 thermal printer"""
    
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
    
    def create_multi_size_image(self, sections):
        """
        Create an image with multiple text sections of different sizes
        
        Args:
            sections: List of dictionaries with keys:
                     - text: The text content
                     - size: Font size in points
                     - align: 'left', 'center', or 'right'
                     - bold: True or False
                     - spacing: Extra spacing after this section in pixels
        """
        try:
            # Calculate total height needed
            total_height = 20  # Initial padding
            section_heights = []
            
            for section in sections:
                font_size = section.get('size', 24)
                text = section.get('text', '')
                spacing = section.get('spacing', 10)
                
                # Create font for measurement
                font = ImageFont.truetype(self.font_path, font_size)
                
                # Wrap text to fit printer width
                max_chars = max(10, int(self.width / (font_size * 0.6)))  # Estimate chars per line
                wrapped_text = []
                for line in text.split('\n'):
                    if line.strip():
                        wrapped_lines = textwrap.wrap(line, width=max_chars)
                        wrapped_text.extend(wrapped_lines)
                    else:
                        wrapped_text.append('')
                
                # Calculate height for this section
                line_height = font_size + 4
                section_height = (len(wrapped_text) * line_height) + spacing
                section_heights.append(section_height)
                total_height += section_height
            
            # Create image with white background
            img = Image.new('L', (self.width, total_height), 255)
            draw = ImageDraw.Draw(img)
            
            # Draw each section
            y_pos = 10  # Start position
            
            for i, section in enumerate(sections):
                font_size = section.get('size', 24)
                text = section.get('text', '')
                align = section.get('align', 'left')
                is_bold = section.get('bold', False)
                
                # Create font
                font = ImageFont.truetype(self.font_path, font_size)
                
                # Wrap text to fit printer width
                max_chars = max(10, int(self.width / (font_size * 0.6)))  # Estimate chars per line
                wrapped_text = []
                for line in text.split('\n'):
                    if line.strip():
                        wrapped_lines = textwrap.wrap(line, width=max_chars)
                        wrapped_text.extend(wrapped_lines)
                    else:
                        wrapped_text.append('')
                
                # Draw each line with proper alignment
                line_height = font_size + 4
                for line in wrapped_text:
                    if align == 'center':
                        text_width = draw.textlength(line, font=font)
                        x_pos = (self.width - text_width) / 2
                    elif align == 'right':
                        text_width = draw.textlength(line, font=font)
                        x_pos = self.width - text_width - 10
                    else:  # left
                        x_pos = 10
                    
                    # Draw text (draw twice for bold)
                    draw.text((x_pos, y_pos), line, font=font, fill=0)
                    if is_bold:
                        draw.text((x_pos+1, y_pos), line, font=font, fill=0)
                    
                    y_pos += line_height
                
                # Add section spacing
                y_pos += section.get('spacing', 10)
            
            return img
        
        except Exception as e:
            print(f"Error creating multi-size image: {e}")
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
    
    def print_multi_size_thai(self, sections):
        """Print Thai text with multiple font sizes"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            # Create multi-size image
            img = self.create_multi_size_image(sections)
            if img is None:
                return False
            
            # Print the image
            return self.print_image(img)
        
        except Exception as e:
            print(f"Error printing multi-size Thai text: {e}")
            return False
    
    def print_receipt_with_sizes(self, title, items, total, footer=None):
        """Print a formatted receipt with different font sizes"""
        if not self.ep_out:
            print("Printer not connected")
            return False
        
        try:
            # Format date and time
            from datetime import datetime
            now = datetime.now()
            date_str = now.strftime("%d/%m/%Y")
            time_str = now.strftime("%H:%M:%S")
            
            # Create sections with different sizes
            sections = [
                {
                    'text': title,
                    'size': 32,
                    'align': 'center',
                    'bold': True,
                    'spacing': 20
                },
                {
                    'text': f"วันที่: {date_str}\nเวลา: {time_str}",
                    'size': 20,
                    'align': 'left',
                    'bold': False,
                    'spacing': 15
                },
                {
                    'text': items,
                    'size': 24,
                    'align': 'left',
                    'bold': False,
                    'spacing': 15
                },
                {
                    'text': f"รวม: {total}",
                    'size': 28,
                    'align': 'right',
                    'bold': True,
                    'spacing': 20
                }
            ]
            
            # Add footer if provided
            if footer:
                sections.append({
                    'text': footer,
                    'size': 20,
                    'align': 'center',
                    'bold': False,
                    'spacing': 10
                })
            
            # Print multi-size receipt
            result = self.print_multi_size_thai(sections)
            
            # Feed and cut
            if result:
                self.feed(1)
                self.cut()
            
            return result
        
        except Exception as e:
            print(f"Error printing receipt with sizes: {e}")
            return False

def test_multi_size_printer():
    """Test the Thai multi-size printer"""
    printer = ThaiMultiSizePrinter()
    
    if not printer.connect():
        print("Failed to connect to printer")
        return False
    
    try:
        # Test multi-size Thai text
        print("Testing Thai text with multiple font sizes...")
        
        sections = [
            {
                'text': 'ร้านกาแฟ',
                'size': 36,
                'align': 'center',
                'bold': True,
                'spacing': 20
            },
            {
                'text': 'รายการสินค้า',
                'size': 28,
                'align': 'center',
                'bold': False,
                'spacing': 15
            },
            {
                'text': 'กาแฟเย็น x1 ฿45.00\nชาเย็น x2 ฿70.00\nเค้กช็อคโกแลต x1 ฿60.00',
                'size': 24,
                'align': 'left',
                'bold': False,
                'spacing': 15
            },
            {
                'text': 'รวม: ฿175.00',
                'size': 30,
                'align': 'right',
                'bold': True,
                'spacing': 20
            },
            {
                'text': 'ขอบคุณที่ใช้บริการ\nกรุณามาอีก',
                'size': 22,
                'align': 'center',
                'bold': False,
                'spacing': 10
            }
        ]
        
        printer.print_multi_size_thai(sections)
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
    parser = argparse.ArgumentParser(description='Thai Multi-Size Printer')
    parser.add_argument('--test', action='store_true', help='Test the printer')
    parser.add_argument('--receipt', action='store_true', help='Print a sample receipt')
    
    args = parser.parse_args()
    
    if args.test:
        test_multi_size_printer()
    elif args.receipt:
        printer = ThaiMultiSizePrinter()
        if printer.connect():
            printer.print_receipt_with_sizes(
                title="ร้านกาแฟ",
                items="กาแฟเย็น x1 ฿45.00\nชาเย็น x2 ฿70.00\nเค้กช็อคโกแลต x1 ฿60.00",
                total="฿175.00",
                footer="ขอบคุณที่ใช้บริการ\nกรุณามาอีก"
            )
            printer.disconnect()
    else:
        print("No action specified. Use --test or --receipt")

if __name__ == "__main__":
    main()
