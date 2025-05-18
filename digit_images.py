#!/usr/bin/env python3
"""
Digit Image Generator for Thermal Printers
Creates clean, printer-friendly digit images that render reliably on thermal printers
"""

from PIL import Image, ImageDraw, ImageFont
import os
import tempfile

class DigitRenderer:
    def __init__(self, digit_size=80, spacing=10, stroke_width=None):
        self.digit_size = digit_size
        self.spacing = spacing
        self.stroke_width = stroke_width or max(3, digit_size // 15)  # Default based on size
        
    def create_digit(self, digit):
        """Create a single digit image"""
        if not digit.isdigit() or len(digit) != 1:
            return None
            
        # Create a white image with proper padding
        border = self.digit_size // 10
        img_size = (self.digit_size + border*2, self.digit_size + border*2)
        img = Image.new('1', img_size, color=1)  # 1=white in binary mode
        draw = ImageDraw.Draw(img)
        
        # Coordinates for drawing
        cx, cy = img_size[0] // 2, img_size[1] // 2  # Center
        width = self.digit_size - border*2
        height = self.digit_size - border*2
        
        # Draw based on digit value
        digit_value = int(digit)
        stroke = self.stroke_width
        
        if digit_value == 0:
            # Draw a rounded rectangle/ellipse for zero
            draw.ellipse(
                (border, border, img_size[0]-border, img_size[1]-border),
                outline=0,  # Black outline
                width=stroke
            )
        elif digit_value == 1:
            # Simple vertical line
            line_x = cx
            draw.line(
                (line_x, border, line_x, img_size[1]-border),
                fill=0,  # Black
                width=stroke*2
            )
        elif digit_value == 2:
            # Top semicircle
            radius = width // 2
            draw.arc(
                (border, border, img_size[0]-border, cy),
                180, 0,
                fill=0,
                width=stroke
            )
            # Diagonal line
            draw.line(
                (img_size[0]-border, cy, border, img_size[1]-border),
                fill=0,
                width=stroke
            )
            # Bottom line
            draw.line(
                (border, img_size[1]-border, img_size[0]-border, img_size[1]-border),
                fill=0,
                width=stroke
            )
        elif digit_value == 3:
            # Top semicircle
            draw.arc(
                (border, border, img_size[0]-border, cy),
                180, 0,
                fill=0,
                width=stroke
            )
            # Bottom semicircle
            draw.arc(
                (border, cy, img_size[0]-border, img_size[1]-border),
                0, 180,
                fill=0,
                width=stroke
            )
        elif digit_value == 4:
            # Vertical line (right)
            draw.line(
                (img_size[0]-border*2, border, img_size[0]-border*2, img_size[1]-border),
                fill=0,
                width=stroke
            )
            # Horizontal middle line
            draw.line(
                (border, cy, img_size[0]-border, cy),
                fill=0,
                width=stroke
            )
            # Vertical line (left, top half)
            draw.line(
                (border*2, border, border*2, cy),
                fill=0,
                width=stroke
            )
        elif digit_value == 5:
            # Top horizontal line
            draw.line(
                (border, border*2, img_size[0]-border, border*2),
                fill=0,
                width=stroke
            )
            # Left vertical line (top half)
            draw.line(
                (border, border*2, border, cy),
                fill=0,
                width=stroke
            )
            # Middle horizontal line
            draw.line(
                (border, cy, img_size[0]-border, cy),
                fill=0,
                width=stroke
            )
            # Bottom semicircle
            draw.arc(
                (border, cy, img_size[0]-border, img_size[1]-border),
                0, 180,
                fill=0,
                width=stroke
            )
        elif digit_value == 6:
            # Full shape
            draw.arc(
                (border, border, img_size[0]-border, img_size[1]-border),
                0, 360,
                fill=0,
                width=stroke
            )
            # Vertical line on left
            draw.line(
                (border+stroke//2, border+height//4, border+stroke//2, img_size[1]-border),
                fill=0,
                width=stroke
            )
        elif digit_value == 7:
            # Top horizontal line
            draw.line(
                (border, border*2, img_size[0]-border, border*2),
                fill=0,
                width=stroke
            )
            # Diagonal line
            draw.line(
                (img_size[0]-border*2, border*2, cx, img_size[1]-border),
                fill=0,
                width=stroke
            )
        elif digit_value == 8:
            # Draw two stacked circles
            draw.ellipse(
                (border, border, img_size[0]-border, cy+border//2),
                outline=0,
                width=stroke
            )
            draw.ellipse(
                (border, cy-border//2, img_size[0]-border, img_size[1]-border),
                outline=0,
                width=stroke
            )
        elif digit_value == 9:
            # Full shape
            draw.arc(
                (border, border, img_size[0]-border, img_size[1]-border),
                0, 360,
                fill=0,
                width=stroke
            )
            # Vertical line on right
            draw.line(
                (img_size[0]-border-stroke//2, border+height//4, img_size[0]-border-stroke//2, img_size[1]-border),
                fill=0,
                width=stroke
            )
        
        return img
        
    def create_number(self, number_str):
        """Create a complete number image from multiple digits"""
        # Handle empty or non-numeric strings
        if not number_str or not any(c.isdigit() for c in number_str):
            number_str = "0"  # Default to 0 if no valid digits
            
        # Filter to digits only
        digits = ''.join(c for c in number_str if c.isdigit())
        
        # Create individual digit images
        digit_images = [self.create_digit(d) for d in digits]
        digit_images = [img for img in digit_images if img is not None]  # Filter any None results
        
        if not digit_images:
            return None
            
        # Calculate combined size
        total_width = sum(img.width for img in digit_images) + self.spacing * (len(digit_images) - 1)
        max_height = max(img.height for img in digit_images)
        
        # Create the combined image
        result = Image.new('1', (total_width, max_height), color=1)  # White background
        
        # Place each digit
        x_position = 0
        for img in digit_images:
            result.paste(img, (x_position, 0))
            x_position += img.width + self.spacing
            
        return result
        
    def create_number_file(self, number_str, directory=None):
        """Create a number image and save it to a temporary file"""
        number_img = self.create_number(number_str)
        if not number_img:
            return None
            
        # Save to temp file
        fd, path = tempfile.mkstemp(suffix='.png', dir=directory)
        os.close(fd)
        number_img.save(path)
        return path

# Convenience function for simple usage
def create_number_image(number_str, digit_size=80, spacing=10):
    """Create a number image with default settings"""
    renderer = DigitRenderer(digit_size=digit_size, spacing=spacing)
    return renderer.create_number(number_str)

# Test function to generate sample digit images
def generate_samples():
    """Generate sample images of all digits"""
    renderer = DigitRenderer(digit_size=60)
    
    # Generate all individual digits
    for i in range(10):
        img = renderer.create_digit(str(i))
        img.save(f"digit_{i}.png")
        print(f"Created digit_{i}.png")
    
    # Generate some sample numbers
    samples = ["123", "456", "789", "42", "007"]
    for num in samples:
        img = renderer.create_number(num)
        if img:
            img.save(f"number_{num}.png")
            print(f"Created number_{num}.png")

if __name__ == "__main__":
    # Test the digit renderer by generating samples
    generate_samples()
"""
Utility to create digit images for thermal printer
This avoids font rendering issues by using pre-drawn digit shapes
"""

from PIL import Image, ImageDraw
import tempfile
import os

def create_digit_image(digit, size=80, border=5):
    """Create an image of a single digit with specified size"""
    # Each digit is a white shape on black background
    img_size = (size + border*2, size + border*2)
    img = Image.new('1', img_size, color=1)  # 1=white in binary mode
    draw = ImageDraw.Draw(img)
    
    # Stroke width
    stroke = max(3, size // 15)
    
    # Calculate center and dimensions
    cx, cy = size//2 + border, size//2 + border
    width, height = size - border*2, size - border*2
    
    # Draw digit based on value
    if digit == '0':
        # Draw a rounded rectangle for zero
        draw.rounded_rectangle(
            (border + stroke, border + stroke, 
             size + border - stroke, size + border - stroke),
            radius=size//4,
            fill=1,  # white
            outline=0,  # black
            width=stroke
        )
    elif digit == '1':
        # Draw a vertical line for 1
        middle_x = cx
        draw.rectangle(
            (middle_x - stroke//2, border, 
             middle_x + stroke//2, size + border),
            fill=0  # black
        )
    elif digit == '2':
        # Top arc
        draw.arc(
            (border, border, 
             size + border, size + border),
            180, 0,  # Top half circle
            fill=0,  # black
            width=stroke
        )
        # Bottom diagonal line
        draw.line(
            (border, cy, size + border, size + border),
            fill=0,  # black
            width=stroke
        )
        # Bottom line
        draw.line(
            (border, size + border, size + border, size + border),
            fill=0,  # black
            width=stroke
        )
    elif digit == '3':
        # Draw a 3 shape: top and bottom rounded parts
        # Top semicircle
        draw.arc(
            (border, border,
             size + border, cy),
            180, 0,
            fill=0,
            width=stroke
        )
        # Bottom semicircle
        draw.arc(
            (border, cy,
             size + border, size + border),
            0, 180,
            fill=0,
            width=stroke
        )
    elif digit == '4':
        # Vertical line on right
        draw.line(
            (size + border - stroke, border, size + border - stroke, size + border),
            fill=0,
            width=stroke
        )
        # Horizontal line in middle
        draw.line(
            (border, cy, size + border, cy),
            fill=0,
            width=stroke
        )
        # Diagonal line on left
        draw.line(
            (border, border, size + border - stroke, cy),
            fill=0,
            width=stroke
        )
    elif digit == '5':
        # Top horizontal line
        draw.line(
            (border, border, size + border, border),
            fill=0,
            width=stroke
        )
        # Left vertical line (top half)
        draw.line(
            (border, border, border, cy),
            fill=0,
            width=stroke
        )
        # Middle horizontal line
        draw.line(
            (border, cy, size + border, cy),
            fill=0,
            width=stroke
        )
        # Bottom arc
        draw.arc(
            (border, cy,
             size + border, size + border),
            0, 180,
            fill=0,
            width=stroke
        )
    elif digit == '6':
        # Top arc
        draw.arc(
            (border, border,
             size + border, cy),
            180, 0,
            fill=0,
            width=stroke
        )
        # Left vertical line
        draw.line(
            (border, border, border, size + border),
            fill=0,
            width=stroke
        )
        # Bottom circle
        draw.ellipse(
            (border, cy,
             size + border, size + border),
            outline=0,
            width=stroke
        )
    elif digit == '7':
        # Top horizontal line
        draw.line(
            (border, border, size + border, border),
            fill=0,
            width=stroke
        )
        # Diagonal line
        draw.line(
            (size + border, border, border + size//2, size + border),
            fill=0,
            width=stroke
        )
    elif digit == '8':
        # Draw two circles for 8
        draw.ellipse(
            (border, border,
             size + border, cy),
            outline=0,
            width=stroke
        )
        draw.ellipse(
            (border, cy - stroke//2,
             size + border, size + border),
            outline=0,
            width=stroke
        )
    elif digit == '9':
        # Top circle
        draw.ellipse(
            (border, border,
             size + border, cy),
            outline=0,
            width=stroke
        )
        # Right vertical line
        draw.line(
            (size + border, border, size + border, size + border),
            fill=0,
            width=stroke
        )
        # Bottom arc
        draw.arc(
            (border, cy,
             size + border, size + border),
            0, 90,
            fill=0,
            width=stroke
        )
    
    return img

def create_number_image(number_str, digit_size=80, spacing=10):
    """Create an image with multiple digits for a number"""
    if not number_str:
        return None
        
    # Handle non-digit characters
    digits = ''.join(c for c in number_str if c.isdigit())
    if not digits:
        return None
    
    # Create individual digit images
    digit_images = [create_digit_image(d, size=digit_size) for d in digits]
    
    # Calculate total width and height
    total_width = sum(img.width for img in digit_images) + spacing * (len(digit_images) - 1)
    max_height = max(img.height for img in digit_images)
    
    # Create a new image to hold all digits
    combined = Image.new('1', (total_width, max_height), color=1)  # 1=white
    
    # Paste each digit image
    x_offset = 0
    for img in digit_images:
        combined.paste(img, (x_offset, 0))
        x_offset += img.width + spacing
    
    return combined

def save_digit_demo():
    """Create a demo image with all digits"""
    # Create images for all digits
    all_digits = "0123456789"
    images = [create_digit_image(d, size=50) for d in all_digits]
    
    # Create a row of all digits
    width = sum(img.width for img in images) + 10 * (len(images) - 1)
    height = max(img.height for img in images)
    
    demo = Image.new('1', (width, height), color=1)
    
    x = 0
    for img in images:
        demo.paste(img, (x, 0))
        x += img.width + 10
        
    # Save the demo
    demo.save("digit_demo.png")
    print("Saved digit demo to digit_demo.png")
    
    # Test numbers
    test_numbers = ["123", "456", "789", "42", "007"]
    for num in test_numbers:
        img = create_number_image(num)
        filename = f"number_{num}.png"
        img.save(filename)
        print(f"Saved {filename}")

if __name__ == "__main__":
    save_digit_demo()
