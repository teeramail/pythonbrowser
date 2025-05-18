#!/usr/bin/env python3
"""
Thai Receipt Generator
Creates properly formatted Thai receipts for thermal printers
"""

from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
import time
from datetime import datetime
# Import both options for number rendering
from digit_images import create_number_image, DigitRenderer

class ThaiReceiptGenerator:
    def __init__(self):
        # Find a suitable Thai font
        self.font_path = self._find_thai_font()
        self.digit_renderer = DigitRenderer(digit_size=70)
        self.receipt_width = 384  # Standard for 58mm thermal printers
        
        # Find a simple font for numbers (monospace/sans-serif)
        self.number_font_path = self._find_number_font()
        
    def _find_thai_font(self):
        """Find an available Thai font from common locations"""
        font_paths = [
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
            "/usr/share/fonts/truetype/thai/TlwgTypo.ttf",
            "/home/mllseminipc/pythonbrowser/THSarabunNew.ttf",
            "/usr/share/fonts/truetype/tlwg/TlwgMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Fallback
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                print(f"Using Thai font: {path}")
                return path
                
        # Last resort fallback
        print("Warning: No suitable font found, using default")
        return None
        
    def _find_number_font(self):
        """Find a simple font for numbers that resembles Firefox print preview"""
        # Look for monospace or simple sans-serif fonts that render clearly on thermal printers
        number_font_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Good fallback
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
        ]
        
        for path in number_font_paths:
            if os.path.exists(path):
                print(f"Using number font: {path}")
                return path
        
        # If no special number font is found, use the same as Thai font
        return self.font_path
    
    def create_receipt(self, service_name, queue_number, timestamp=None, waiting_count="รอ 20 คิว"):
        """
        Create a complete receipt image with Thai text
        
        Args:
            service_name: Department or service name (e.g., "ฝ่ายสินเชื่อ")
            queue_number: Queue number as string (e.g., "21")
            timestamp: Optional timestamp (defaults to current date/time)
            waiting_count: Waiting message (e.g., "20คิว")
            
        Returns:
            Path to the generated image file
        """
        try:
            # Create fonts in different sizes (increased by 30% total)
            title_font = ImageFont.truetype(self.font_path, 33)  # Service name (Thai font)
            
            # Use simpler font for queue numbers and date/time
            queue_font = ImageFont.truetype(self.number_font_path, 92)  # Large, simple font for queue numbers
            date_font = ImageFont.truetype(self.number_font_path, 24)   # Date/time with simple font
            
            # Use Thai font for waiting count (same as department name)
            wait_font = ImageFont.truetype(self.font_path, 24)   # Waiting count with Thai font
            
            # Handle empty queue number
            if not queue_number or queue_number.strip() == "":
                queue_number = "0"
                
            # Use current time if not provided
            if not timestamp:
                timestamp = datetime.now().strftime("%d/%m/ %H:%M รอ")
                
            # Calculate sizes for layout
            temp_img = Image.new('RGB', (self.receipt_width, 500), color='white')
            draw = ImageDraw.Draw(temp_img)
            
            # Pre-calculate text sizes
            title_bbox = draw.textbbox((0, 0), service_name, font=title_font)
            title_height = title_bbox[3] - title_bbox[1]
            
            # Calculate queue number size with our simpler font
            queue_bbox = draw.textbbox((0, 0), queue_number, font=queue_font)
            queue_width = queue_bbox[2] - queue_bbox[0]
            queue_height = queue_bbox[3] - queue_bbox[1]
            
            # Text sizes for remaining elements
            date_bbox = draw.textbbox((0, 0), timestamp, font=date_font)
            date_height = date_bbox[3] - date_bbox[1]
            
            wait_bbox = draw.textbbox((0, 0), waiting_count, font=wait_font)
            wait_height = wait_bbox[3] - wait_bbox[1]
            
            # Calculate total receipt height
            total_height = (
                30 +                 # Top margin
                title_height + 20 +  # Service name + spacing
                queue_height + 20 +  # Queue number + spacing
                date_height + 15 +   # Date + spacing
                wait_height + 30     # Waiting count + bottom margin
            )
            
            # Create the actual receipt image
            receipt = Image.new('RGB', (self.receipt_width, total_height), color='white')
            draw = ImageDraw.Draw(receipt)
            
            # Start drawing from the top
            y_pos = 15
            
            # 1. Draw service name
            title_width = title_bbox[2] - title_bbox[0]
            x_pos = (self.receipt_width - title_width) // 2  # Center horizontally
            draw.text((x_pos, y_pos), service_name, font=title_font, fill='black')
            y_pos += title_height + 20
            
            # 2. Draw queue number using our simple font
            x_pos = (self.receipt_width - queue_width) // 2
            draw.text((x_pos, y_pos), queue_number, font=queue_font, fill='black')
            y_pos += queue_height + 20
            
            # 3. Draw timestamp
            date_width = date_bbox[2] - date_bbox[0]
            x_pos = (self.receipt_width - date_width) // 2
            draw.text((x_pos, y_pos), timestamp, font=date_font, fill='black')
            y_pos += date_height + 25  # Add more space (25px instead of 15px) before the last line
            
            # 4. Draw waiting count with mixed fonts (Thai text in Thai font, numbers in simple font)
            # First, we need to split the waiting count into parts
            if waiting_count.startswith("รอ") and "คิว" in waiting_count:
                # Split the "รอ 20 คิว" into ["รอ", "20", "คิว"]
                parts = waiting_count.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    # Handle "รอ" "20" "คิว" format with 3 parts
                    thai_prefix = parts[0] + " "  # "รอ "
                    number_part = parts[1]       # "20"
                    thai_suffix = " " + parts[2]  # " คิว"
                else:
                    # Fall back to regular text if format doesn't match
                    draw.text((self.receipt_width//2, y_pos), waiting_count, 
                              font=wait_font, anchor="mt", fill='black')
                    
                # Calculate widths for positioning
                prefix_bbox = draw.textbbox((0, 0), thai_prefix, font=wait_font)
                prefix_width = prefix_bbox[2] - prefix_bbox[0]
                
                number_bbox = draw.textbbox((0, 0), number_part, font=date_font)  # Use simple font for number
                number_width = number_bbox[2] - number_bbox[0]
                
                suffix_bbox = draw.textbbox((0, 0), thai_suffix, font=wait_font)
                suffix_width = suffix_bbox[2] - suffix_bbox[0]
                
                total_width = prefix_width + number_width + suffix_width
                
                # Calculate starting position to center the whole text
                start_x = (self.receipt_width - total_width) // 2
                
                # Draw each part with the appropriate font
                draw.text((start_x, y_pos), thai_prefix, font=wait_font, fill='black')
                draw.text((start_x + prefix_width, y_pos), number_part, font=date_font, fill='black')  # Number with simple font
                draw.text((start_x + prefix_width + number_width, y_pos), thai_suffix, font=wait_font, fill='black')
            else:
                # If waiting count format doesn't match the expected format, draw it normally
                wait_bbox = draw.textbbox((0, 0), waiting_count, font=wait_font)
                wait_width = wait_bbox[2] - wait_bbox[0]
                x_pos = (self.receipt_width - wait_width) // 2
                draw.text((x_pos, y_pos), waiting_count, font=wait_font, fill='black')
            
            # Save to a temporary file
            fd, path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            receipt.save(path)
            print(f"Created Thai receipt at: {path}")
            
            return path
            
        except Exception as e:
            print(f"Error creating Thai receipt: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    def extract_queue_info(self, html_content):
        """Extract queue details from page content"""
        import re
        
        # Extract queue number - look for larger digits
        queue_pattern = r'(?:<h1>|<div[^>]+>)\s*(\d{1,3})\s*(?:</h1>|</div>)'
        queue_match = re.search(queue_pattern, html_content)
        if not queue_match:
            # Fall back to any digits
            queue_match = re.search(r'[^\d](\d{1,3})[^\d]', html_content)
            
        queue_number = queue_match.group(1) if queue_match else "0"
        
        # Extract service name - common Thai department names
        dept_pattern = r'(?:<h[1-3]>|<div[^>]+>)\s*(ฝ่าย\w+)\s*(?:</h[1-3]>|</div>)'
        dept_match = re.search(dept_pattern, html_content)
        service_name = dept_match.group(1) if dept_match else "ฝ่ายสินเชื่อ"
        
        # Extract date/time format
        date_pattern = r'(\d{1,2}/\d{1,2}/\s*\d{1,2}:\d{1,2})'
        date_match = re.search(date_pattern, html_content)
        timestamp = date_match.group(1) if date_match else None
        
        # Extract waiting count
        wait_pattern = r'รอ\s*(\d+)\s*คิว'
        wait_match = re.search(wait_pattern, html_content)
        waiting_count = f"{wait_match.group(1)}คิว" if wait_match else "20คิว"
        
        return {
            "queue_number": queue_number,
            "service_name": service_name,
            "timestamp": timestamp,
            "waiting_count": waiting_count
        }

# Direct test function
if __name__ == "__main__":
    generator = ThaiReceiptGenerator()
    
    # Test receipt generation
    receipt_path = generator.create_receipt(
        service_name="ฝ่ายสินเชื่อ",
        queue_number="21",
        timestamp="16/05/ 05:12 รอ",
        waiting_count="20คิว"
    )
    
    if receipt_path:
        print(f"Receipt created at {receipt_path}")
