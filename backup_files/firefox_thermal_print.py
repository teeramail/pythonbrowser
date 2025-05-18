#!/usr/bin/env python3
"""
Firefox Thermal Print - Opens Firefox with the correct print settings for a 58mm thermal printer
"""

import os
import sys
import subprocess
import time
import argparse
from datetime import datetime

def create_custom_receipt(template_path, output_path, title, items, total, footer):
    """Create a custom receipt HTML file from the template"""
    try:
        # Read the template
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M")
        
        # Format items HTML
        items_html = ""
        for item in items:
            name = item.get('name', '')
            price = item.get('price', 0)
            qty = item.get('qty', 1)
            
            items_html += f"""
            <div class="item">
                <span class="item-name">{name} x{qty}</span>
                <span class="item-price">฿{price:.2f}</span>
            </div>
            """
        
        # Replace placeholders in template
        content = template
        content = content.replace('ร้านกาแฟ', title)
        content = content.replace('<div class="content">\n            <div class="item">\n                <span class="item-name">กาแฟเย็น x1</span>\n                <span class="item-price">฿45.00</span>\n            </div>\n            <div class="item">\n                <span class="item-name">ชาเย็น x2</span>\n                <span class="item-price">฿70.00</span>\n            </div>\n            <div class="item">\n                <span class="item-name">เค้กช็อคโกแลต x1</span>\n                <span class="item-price">฿60.00</span>\n            </div>\n        </div>', f'<div class="content">{items_html}</div>')
        content = content.replace('<span>฿175.00</span>', f'<span>฿{total:.2f}</span>')
        content = content.replace('ขอบคุณที่ใช้บริการ\n            <br>\n            กรุณามาอีก', footer.replace('\n', '<br>'))
        content = content.replace('<span>13/05/2025</span>', f'<span>{date_str}</span>')
        content = content.replace('<span>14:20</span>', f'<span>{time_str}</span>')
        
        # Write the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Custom receipt created at: {output_path}")
        return True
    
    except Exception as e:
        print(f"Error creating custom receipt: {e}")
        return False

def open_firefox_with_print_settings(html_file):
    """Open Firefox with the HTML file and print settings for 58mm thermal printer"""
    try:
        # Get absolute path to the HTML file
        abs_path = os.path.abspath(html_file)
        file_url = f"file://{abs_path}"
        
        # Firefox command with print settings
        # -P "thermal" uses a profile named "thermal" if it exists
        # -print-settings "paper_size=3x5in" sets the paper size
        cmd = [
            "firefox",
            "-P", "default",  # Use default profile
            file_url
        ]
        
        print(f"Opening Firefox with: {file_url}")
        process = subprocess.Popen(cmd)
        
        print("\nPrinting Instructions:")
        print("1. When Firefox opens, press Ctrl+P to open the print dialog")
        print("2. In the print dialog, set the following:")
        print("   - Destination: Your thermal printer (ThermalPOS)")
        print("   - Paper size: Custom (58mm x 100mm)")
        print("   - Margins: Minimum")
        print("   - Scale: 100%")
        print("   - Options: Background graphics checked")
        print("3. Click Print")
        
        return True
    
    except Exception as e:
        print(f"Error opening Firefox: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Firefox Thermal Print')
    parser.add_argument('--title', type=str, default='ร้านกาแฟ', help='Receipt title')
    parser.add_argument('--items', type=str, help='Items in JSON format: [{"name":"Item1","price":10,"qty":1}]')
    parser.add_argument('--total', type=float, help='Total amount')
    parser.add_argument('--footer', type=str, default='ขอบคุณที่ใช้บริการ', help='Footer text')
    parser.add_argument('--template', type=str, help='Path to custom HTML template')
    
    args = parser.parse_args()
    
    # Default template path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "thermal_receipt_template.html")
    
    # Use custom template if provided
    if args.template and os.path.exists(args.template):
        template_path = args.template
    
    # Output path for the custom receipt
    output_path = os.path.join(script_dir, "custom_receipt.html")
    
    # Parse items if provided
    items = []
    if args.items:
        import json
        try:
            items = json.loads(args.items)
        except:
            print("Error parsing items JSON. Using sample items.")
            items = [
                {"name": "กาแฟเย็น", "price": 45.00, "qty": 1},
                {"name": "ชาเย็น", "price": 35.00, "qty": 2},
                {"name": "เค้กช็อคโกแลต", "price": 60.00, "qty": 1}
            ]
    else:
        # Sample items
        items = [
            {"name": "กาแฟเย็น", "price": 45.00, "qty": 1},
            {"name": "ชาเย็น", "price": 35.00, "qty": 2},
            {"name": "เค้กช็อคโกแลต", "price": 60.00, "qty": 1}
        ]
    
    # Calculate total if not provided
    if not args.total:
        total = sum(item["price"] * item["qty"] for item in items)
    else:
        total = args.total
    
    # Create custom receipt
    if create_custom_receipt(template_path, output_path, args.title, items, total, args.footer):
        # Open Firefox with print settings
        open_firefox_with_print_settings(output_path)

if __name__ == "__main__":
    main()
