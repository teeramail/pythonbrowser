#!/usr/bin/env python3
"""Thai Receipt Printing Test

This script tests both direct Thai text printing and image-based Thai receipt printing
with proper digit rendering for reliable output on 58mm thermal printers.
"""

from thermal_printer import get_printer
from thai_receipt import ThaiReceiptGenerator
import os
import time
from datetime import datetime

# Test settings
SERVICE_NAME = "ฝ่ายสินเชื่อ"  # Department name in Thai
QUEUE_NUMBER = "21"         # Queue number to print
TIMESTAMP = "16/05/ 15:45 รอ"  # Date/time with Thai 'waiting' suffix
WAITING_COUNT = "รอ 20 คิว"    # Waiting count in format 'waiting 20 queues' in Thai

def test_direct_thai_text():
    """Test printing Thai receipt as direct text"""
    print("\n1. Testing direct Thai text printing...")
    
    # Thai test content
    title = SERVICE_NAME
    content = f"\n{QUEUE_NUMBER}\n\n{TIMESTAMP}\n{WAITING_COUNT}"
    footer = "Thank you!"
    
    # Print using the thermal printer
    printer = get_printer()
    
    try:
        if printer.connect():
            print("Connected to printer, sending Thai text...")
            success = printer.print_receipt(title, content, footer)
            printer.disconnect()
            
            if success:
                print("Thai text printed successfully!")
                return True
            else:
                print("Failed to print Thai text")
                return False
        else:
            print("Failed to connect to printer")
            return False
    except Exception as e:
        print(f"Error in test_direct_thai_text: {e}")
        return False

def test_image_receipt():
    """Test printing Thai receipt as rendered image"""
    print("\n2. Testing Thai receipt image printing...")
    
    # Create receipt generator
    generator = ThaiReceiptGenerator()
    
    try:
        # Generate receipt image
        image_path = generator.create_receipt(
            service_name=SERVICE_NAME,
            queue_number=QUEUE_NUMBER,
            timestamp=TIMESTAMP,
            waiting_count=WAITING_COUNT
        )
        
        if not image_path or not os.path.exists(image_path):
            print("Failed to create Thai receipt image")
            return False
            
        # Print the image
        printer = get_printer()
        if printer.connect():
            print(f"Printing Thai receipt image: {image_path}")
            success = printer.print_image(image_path)
            printer.disconnect()
            
            # Clean up temp file
            try:
                os.unlink(image_path)
            except Exception as e:
                print(f"Warning: Could not remove temp file: {e}")
                
            if success:
                print("Thai receipt image printed successfully!")
                return True
            else:
                print("Failed to print Thai receipt image")
                return False
        else:
            print("Failed to connect to printer")
            return False
    except Exception as e:
        print(f"Error in test_image_receipt: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test both printing methods
    direct_success = test_direct_thai_text()
    
    # Wait before next test
    time.sleep(2)
    
    image_success = test_image_receipt()
    
    if direct_success and image_success:
        print("\nAll tests passed successfully!")
    elif direct_success:
        print("\nOnly direct text printing succeeded.")
    elif image_success:
        print("\nOnly image printing succeeded.")
    else:
        print("\nAll tests failed.")

"""
Thai Character Print Test - This script tests printing Thai characters to the thermal printer
"""

from thermal_printer import get_printer
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
import time
from datetime import datetime

# Thai test text
thai_title = "ทดสอบการพิมพ์"  # "Print Test" in Thai
thai_content = """
รายการที่ 1............฿100.00
รายการที่ 2............฿150.00
รายการที่ 3............฿200.00
-----------------------
รวม..................฿450.00
"""  # Receipt items in Thai

thai_footer = "ขอบคุณที่ใช้บริการ"  # "Thank you for your service" in Thai

def test_thai_printing():
    """Test printing Thai characters to the thermal printer"""
    print("Testing Thai character printing...")
    
    printer = get_printer()
    if printer.connect():
        print("Connected to printer, sending Thai text...")
        success = printer.print_receipt(thai_title, thai_content, thai_footer)
        printer.disconnect()
        
        if success:
            print("Thai text printed successfully!")
            return True
        else:
            print("Failed to print Thai text")
            return False
    else:
        print("Failed to connect to printer")
        return False

def create_receipt_image(service_name="ฝ่ายสินเชื่อ", queue_number="21", timestamp=None, waiting_count="20คิว"):
    """Create a complete receipt image with Thai text in the same format as the screenshot"""
    try:
        # Find a suitable Thai font
        font_paths = [
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
            "/usr/share/fonts/truetype/thai/TlwgTypo.ttf",
            "/home/mllseminipc/pythonbrowser/THSarabunNew.ttf",  # Check if you have this custom font
            "/usr/share/fonts/truetype/tlwg/TlwgMono.ttf"
        ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                print(f"Using Thai font: {path}")
                break
                
        if not font_path:
            print("No Thai font found, using default")
            # Try to use a default system font as fallback
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            
        # Create an image with the right size for a 58mm receipt (about 384 pixels wide)
        width = 384
        
        # Create fonts in different sizes
        title_font = ImageFont.truetype(font_path, 25)      # Service name font
        queue_font = ImageFont.truetype(font_path, 80)      # Large font for queue number
        date_font = ImageFont.truetype(font_path, 18)       # Smaller font for date
        wait_font = ImageFont.truetype(font_path, 18)       # Font for waiting count
        
        # Create a temporary image to measure text heights
        temp_img = Image.new('RGB', (width, 500), color='white')
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Calculate heights for each element
        title_bbox = temp_draw.textbbox((0, 0), service_name, font=title_font)
        title_height = title_bbox[3] - title_bbox[1]
        
        queue_bbox = temp_draw.textbbox((0, 0), queue_number, font=queue_font)
        queue_height = queue_bbox[3] - queue_bbox[1]
        
        # Use provided timestamp or current time
        if not timestamp:
            timestamp = datetime.now().strftime("%d/%m/ %H:%M รอ")
            
        date_bbox = temp_draw.textbbox((0, 0), timestamp, font=date_font)
        date_height = date_bbox[3] - date_bbox[1]
        
        wait_bbox = temp_draw.textbbox((0, 0), waiting_count, font=wait_font)
        wait_height = wait_bbox[3] - wait_bbox[1]
        
        # Calculate total height with spacing
        total_height = title_height + queue_height + date_height + wait_height + 80  # Add padding
        
        # Create the actual image
        image = Image.new('RGB', (width, total_height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Current Y position for drawing
        y_position = 20
        
        # Draw the service name centered
        title_bbox = draw.textbbox((0, 0), service_name, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, y_position), service_name, font=title_font, fill='black')
        y_position += title_height + 20
        
        # Draw the queue number large and centered
        queue_bbox = draw.textbbox((0, 0), queue_number, font=queue_font)
        queue_width = queue_bbox[2] - queue_bbox[0]
        draw.text(((width - queue_width) // 2, y_position), queue_number, font=queue_font, fill='black')
        y_position += queue_height + 15
        
        # Draw the timestamp centered
        date_bbox = draw.textbbox((0, 0), timestamp, font=date_font)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(((width - date_width) // 2, y_position), timestamp, font=date_font, fill='black')
        y_position += date_height + 15
        
        # Draw waiting count centered
        wait_bbox = draw.textbbox((0, 0), waiting_count, font=wait_font)
        wait_width = wait_bbox[2] - wait_bbox[0]
        draw.text(((width - wait_width) // 2, y_position), waiting_count, font=wait_font, fill='black')
        
        # Save to a temporary file
        fd, path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        image.save(path)
        print(f"Thai receipt image created at {path}")
        return path
        
    except Exception as e:
        print(f"Error creating Thai receipt image: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_thai_image_printing():
    """Test printing Thai receipt as an image"""
    print("\n=== Testing Thai receipt image printing ===")
    
    try:
        # Generate the receipt image
        service_name = "ฝ่ายสินเชื่อ"  # Example department name
        queue_number = "21"  # Plain digits for clear display
        timestamp = "16/05/ 05:12 รอ"
        waiting_count = "20คิว"
        
        image_path = create_receipt_image(service_name, queue_number, timestamp, waiting_count)
        if not image_path:
            print("Failed to create Thai receipt image")
            return False
            
        # Print the image
        print("Printing Thai receipt image...")
        printer = get_printer()
        if printer.connect():
            success = printer.print_image(image_path)
            printer.disconnect()
            
            # Clean up the temporary image
            try:
                os.unlink(image_path)
            except Exception as e:
                print(f"Error removing temp file: {e}")
                
            if success:
                print("Thai receipt image printed successfully!")
                return True
            else:
                print("Failed to print Thai receipt image")
                return False
        else:
            print("Failed to connect to printer")
            return False
    except Exception as e:
        print(f"Error in test_thai_image_printing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n1. Testing Thai text printing directly...")
    test_thai_printing()
    
    # Wait a moment before the second test
    time.sleep(1)
    
    print("\n2. Testing Thai receipt image printing...")
    test_thai_image_printing()
