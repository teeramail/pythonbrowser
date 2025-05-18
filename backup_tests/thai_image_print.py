#!/usr/bin/env python3
"""
Thai Image Print - Converts Thai text to an image and prints it to a thermal printer
This bypasses character encoding issues by printing images instead of text
"""

import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont
from thermal_printer import ThermalPrinter, ESC, GS

class ThaiImagePrinter:
    def __init__(self):
        self.printer = ThermalPrinter()
        self.width = 384  # Standard width for 58mm printer (in pixels)
        self.font_path = "/usr/share/fonts/truetype/thai/Garuda.ttf"  # Default Thai font
        
        # Check if the default Thai font exists, otherwise try to find a suitable font
        if not os.path.exists(self.font_path):
            possible_paths = [
                "/usr/share/fonts/truetype/tlwg/Garuda.ttf",
                "/usr/share/fonts/truetype/tlwg/TlwgMono.ttf",
                "/usr/share/fonts/truetype/tlwg/Norasi.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.font_path = path
                    break
            
            if not os.path.exists(self.font_path):
                print("Warning: Could not find a suitable Thai font. Text may not display correctly.")
                self.font_path = None
    
    def connect(self):
        """Connect to the thermal printer"""
        return self.printer.connect()
    
    def disconnect(self):
        """Disconnect from the printer"""
        self.printer.disconnect()
    
    def create_text_image(self, text, font_size=24, is_bold=False, align="left"):
        """Convert text to an image"""
        # Calculate image height based on text length and line breaks
        lines = text.count('\n') + 1
        estimated_height = lines * (font_size + 5)
        
        # Create a new image with white background
        img = Image.new('1', (self.width, estimated_height), color=255)
        draw = ImageDraw.Draw(img)
        
        # Load font
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font = ImageFont.load_default()
        except Exception as e:
            print(f"Error loading font: {e}")
            font = ImageFont.load_default()
        
        # Draw text on image
        draw.text((10, 10), text, font=font, fill=0)
        
        # Crop image to remove extra white space
        # Get the bounding box of the text
        bbox = img.getbbox()
        if bbox:
            # Add some padding
            padding = 20
            bbox = (max(0, bbox[0] - padding), 
                   max(0, bbox[1] - padding),
                   min(self.width, bbox[2] + padding),
                   min(estimated_height, bbox[3] + padding))
            img = img.crop(bbox)
        
        return img
    
    def print_image(self, image):
        """Print an image to the thermal printer"""
        if not self.printer.is_connected:
            if not self.connect():
                return False
        
        try:
            # Ensure image is correct mode
            if image.mode != '1':
                image = image.convert('1')
            
            # Resize image to fit printer width if needed
            if image.width != self.width:
                ratio = self.width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((self.width, new_height))
            
            # Convert image to printer format
            pixels = list(image.getdata())
            
            # Calculate bytes per line
            bytes_per_line = self.width // 8
            
            # Initialize printer
            self.printer.ep_out.write(bytes([ESC, 0x40]))  # ESC @ - Initialize printer
            
            # Set line spacing to 0
            self.printer.ep_out.write(bytes([ESC, 0x33, 0]))
            
            # Print image line by line
            for y in range(0, image.height, 24):
                # Set bitmap mode
                self.printer.ep_out.write(bytes([ESC, 0x2A, 33, self.width % 256, self.width // 256]))
                
                # Print each line of the image
                for x in range(self.width):
                    bits = 0
                    for b in range(24):
                        if y + b < image.height and x < image.width:
                            if pixels[(y + b) * image.width + x] == 0:  # Black pixel
                                bits |= 1 << (7 - (b % 8))
                        if b % 8 == 7 or b == 23:
                            self.printer.ep_out.write(bytes([bits]))
                            bits = 0
                
                # Line feed
                self.printer.ep_out.write(bytes([10]))
            
            # Cut paper
            self.printer.ep_out.write(bytes([GS, 0x56, 0x00]))
            
            return True
            
        except Exception as e:
            print(f"Error printing image: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_thai_receipt(self, title, items, total, footer=None):
        """Print a Thai receipt with items and total"""
        if not self.connect():
            return False
        
        try:
            # Create title image
            title_img = self.create_text_image(title, font_size=28, is_bold=True, align="center")
            self.print_image(title_img)
            
            # Create content image with items
            content = ""
            for item in items:
                name = item.get('name', '')
                price = item.get('price', 0)
                qty = item.get('qty', 1)
                
                content += f"{name} x{qty}".ljust(20)
                content += f"฿{price:.2f}".rjust(10) + "\n"
            
            # Add separator
            content += "-" * 32 + "\n"
            
            # Add total
            content += "รวมทั้งสิ้น:".ljust(20)
            content += f"฿{total:.2f}".rjust(10) + "\n"
            
            # Print content
            content_img = self.create_text_image(content, font_size=24)
            self.print_image(content_img)
            
            # Print footer if provided
            if footer:
                footer_img = self.create_text_image(footer, font_size=22, align="center")
                self.print_image(footer_img)
            
            self.disconnect()
            return True
            
        except Exception as e:
            print(f"Error printing Thai receipt: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_thai_image_printing():
    """Test the Thai image printing functionality"""
    print("Starting Thai image printing test...")
    
    printer = ThaiImagePrinter()
    
    # Sample receipt data
    title = "ร้านกาแฟ บ้านไทย"
    items = [
        {'name': 'กาแฟเย็น', 'price': 45.00, 'qty': 1},
        {'name': 'ชาเขียว', 'price': 40.00, 'qty': 2},
        {'name': 'น้ำส้ม', 'price': 35.00, 'qty': 1}
    ]
    total = sum(item['price'] * item['qty'] for item in items)
    footer = "ขอบคุณที่ใช้บริการ\nวันที่: 13/05/2025"
    
    success = printer.print_thai_receipt(title, items, total, footer)
    
    if success:
        print("Thai image receipt printed successfully!")
    else:
        print("Failed to print Thai image receipt")
    
    return success

if __name__ == "__main__":
    if test_thai_image_printing():
        print("Test completed successfully")
    else:
        print("Test failed")
