#!/usr/bin/env python3
"""
Print Small Image - Prints a small image to the 58mm thermal printer
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
from thermal_printer import ThermalPrinter, ESC, GS

def create_small_logo():
    """Create a very small logo image for testing"""
    # Create a tiny 200x50 image (half the height)
    img = Image.new('1', (200, 50), color=255)
    draw = ImageDraw.Draw(img)
    
    # Draw a simple logo
    draw.rectangle([(20, 5), (180, 45)], outline=0)
    draw.ellipse([(60, 10), (140, 40)], outline=0)
    
    # Try to load a font for text
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, 18)  # Smaller font
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    # Add text
    draw.text((75, 18), "LOGO", font=font, fill=0)
    
    return img

def create_small_thai_text():
    """Create a very small image with Thai text"""
    # Create a tiny image
    img = Image.new('1', (250, 40), color=255)  # Half the height
    draw = ImageDraw.Draw(img)
    
    # Try to load a Thai font
    try:
        possible_paths = [
            "/usr/share/fonts/truetype/thai/Garuda.ttf",
            "/usr/share/fonts/truetype/tlwg/Garuda.ttf",
            "/usr/share/fonts/truetype/tlwg/TlwgMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        
        font_path = None
        for path in possible_paths:
            if os.path.exists(path):
                font_path = path
                break
        
        if font_path:
            font = ImageFont.truetype(font_path, 18)  # Smaller font
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    # Add Thai text (just one line to save paper)
    draw.text((10, 10), "สวัสดี ยินดีต้อนรับ", font=font, fill=0)
    
    return img

def print_image(image):
    """Print an image to the thermal printer"""
    printer = ThermalPrinter()
    
    if not printer.connect():
        print("Failed to connect to printer")
        return False
    
    try:
        # Ensure image is correct mode
        if image.mode != '1':
            image = image.convert('1')
        
        # Resize image to fit printer width if needed
        printer_width = 384  # Standard width for 58mm printer (in pixels)
        if image.width > printer_width:
            ratio = printer_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((printer_width, new_height))
        
        # Center the image if it's smaller than printer width
        if image.width < printer_width:
            new_img = Image.new('1', (printer_width, image.height), color=255)
            paste_x = (printer_width - image.width) // 2
            new_img.paste(image, (paste_x, 0))
            image = new_img
        
        # Convert image to printer format
        pixels = list(image.getdata())
        
        # Calculate bytes per line
        bytes_per_line = printer_width // 8
        
        # Initialize printer
        printer.ep_out.write(bytes([ESC, 0x40]))  # ESC @ - Initialize printer
        
        # Set line spacing to 0
        printer.ep_out.write(bytes([ESC, 0x33, 0]))
        
        # Print image line by line
        for y in range(0, image.height, 24):
            # Set bitmap mode
            printer.ep_out.write(bytes([ESC, 0x2A, 33, printer_width % 256, printer_width // 256]))
            
            # Print each line of the image
            for x in range(printer_width):
                bits = 0
                for b in range(24):
                    if y + b < image.height and x < image.width:
                        if pixels[(y + b) * image.width + x] == 0:  # Black pixel
                            bits |= 1 << (7 - (b % 8))
                    if b % 8 == 7 or b == 23:
                        printer.ep_out.write(bytes([bits]))
                        bits = 0
            
            # Line feed
            printer.ep_out.write(bytes([10]))
        
        # Cut paper immediately without feeding extra lines
        printer.ep_out.write(bytes([GS, 0x56, 0x00]))
        
        printer.disconnect()
        return True
        
    except Exception as e:
        print(f"Error printing image: {e}")
        import traceback
        traceback.print_exc()
        printer.disconnect()
        return False

def test_small_image_printing():
    """Test printing small images to the thermal printer"""
    print("Creating and printing a small logo...")
    logo = create_small_logo()
    if print_image(logo):
        print("Logo printed successfully!")
    else:
        print("Failed to print logo")
        return False
    
    print("\nCreating and printing small Thai text...")
    thai_text = create_small_thai_text()
    if print_image(thai_text):
        print("Thai text printed successfully!")
    else:
        print("Failed to print Thai text")
        return False
    
    return True

if __name__ == "__main__":
    if test_small_image_printing():
        print("All tests completed successfully")
    else:
        print("Tests failed")
