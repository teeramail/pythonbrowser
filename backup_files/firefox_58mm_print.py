#!/usr/bin/env python3
"""
Firefox 58mm Print - Opens Firefox with the correct print settings for a 58mm thermal printer
"""

import os
import sys
import subprocess
import time
import argparse
from datetime import datetime
import json

def create_custom_receipt(items, total, title="ร้านกาแฟ", footer="ขอบคุณที่ใช้บริการ"):
    """Create a custom receipt HTML file with the correct 58mm width"""
    try:
        # Output path for the custom receipt
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "custom_receipt_58mm.html")
        
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
        
        # Create HTML content with strict 58mm width settings
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>58mm Thermal Receipt</title>
    <link rel="stylesheet" href="thermal_print_58mm.css">
    <style>
        @page {{
            size: 5.8cm auto !important;  /* Width: 5.8cm, Height: auto */
            margin: 0.1cm !important;      /* Minimal margins */
        }}
        
        @media print {{
            html, body {{
                width: 5.6cm !important;  /* 5.8cm - 0.2cm margins */
                margin: 0 !important;
                padding: 0 !important;
                font-family: 'Noto Sans Thai', sans-serif !important;
            }}
            
            .no-print {{
                display: none !important;
            }}
        }}
        
        body {{
            width: 5.6cm;
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans Thai', sans-serif;
            font-size: 10pt;
            background-color: white;
        }}
        
        .receipt {{
            width: 100%;
        }}
        
        .header {{
            text-align: center;
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 14pt;
        }}
        
        .subheader {{
            text-align: center;
            font-size: 12pt;
            margin-bottom: 5px;
        }}
        
        .date-time {{
            font-size: 9pt;
            margin-bottom: 5px;
        }}
        
        .content {{
            margin: 5px 0;
        }}
        
        .item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 3px;
        }}
        
        .item-name {{
            flex: 2;
        }}
        
        .item-price {{
            flex: 1;
            text-align: right;
        }}
        
        .total {{
            display: flex;
            justify-content: space-between;
            font-weight: bold;
            margin-top: 5px;
            font-size: 12pt;
            border-top: 1px dashed #000;
            padding-top: 3px;
        }}
        
        .footer {{
            text-align: center;
            font-size: 9pt;
            margin-top: 10px;
        }}
        
        .print-button {{
            display: block;
            margin: 10px auto;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14pt;
            font-family: 'Noto Sans Thai', sans-serif;
        }}
    </style>
</head>
<body>
    <div class="receipt">
        <div class="header">
            {title}
        </div>
        
        <div class="subheader">
            ใบเสร็จรับเงิน
        </div>
        
        <div class="date-time">
            <div class="item">
                <span>วันที่:</span>
                <span>{date_str}</span>
            </div>
            <div class="item">
                <span>เวลา:</span>
                <span>{time_str}</span>
            </div>
        </div>
        
        <div class="content">
            {items_html}
        </div>
        
        <div class="total">
            <span>รวม:</span>
            <span>฿{total:.2f}</span>
        </div>
        
        <div class="footer">
            {footer.replace(chr(10), '<br>')}
        </div>
    </div>
    
    <button class="print-button no-print" onclick="printWithSettings()">พิมพ์ใบเสร็จ</button>
    
    <script>
        function printWithSettings() {{
            // Set print settings
            const mediaQueryList = window.matchMedia('print');
            mediaQueryList.addListener(function(mql) {{
                if(mql.matches) {{
                    document.body.style.width = '5.6cm';
                }}
            }});
            
            // Print the page
            window.print();
        }}
        
        // Auto-print after 1 second
        setTimeout(function() {{
            printWithSettings();
        }}, 1000);
    </script>
</body>
</html>
        """
        
        # Write the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Custom receipt created at: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error creating custom receipt: {e}")
        return None

def open_firefox_with_print_settings(html_file):
    """Open Firefox with the HTML file and print settings for 58mm thermal printer"""
    try:
        # Get absolute path to the HTML file
        abs_path = os.path.abspath(html_file)
        file_url = f"file://{abs_path}"
        
        # Firefox command
        cmd = [
            "firefox",
            "-new-window",
            file_url
        ]
        
        print(f"Opening Firefox with: {file_url}")
        process = subprocess.Popen(cmd)
        
        print("\nPrinting Instructions:")
        print("1. When Firefox opens, press Ctrl+P to open the print dialog")
        print("2. In the print dialog, set the following:")
        print("   - Destination: Your thermal printer (ThermalPOS)")
        print("   - Paper size: Custom (5.8cm x 10cm)")
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
    parser = argparse.ArgumentParser(description='Firefox 58mm Print')
    parser.add_argument('--title', type=str, default='ร้านกาแฟ', help='Receipt title')
    parser.add_argument('--items', type=str, help='Items in JSON format: [{"name":"Item1","price":10,"qty":1}]')
    parser.add_argument('--total', type=float, help='Total amount')
    parser.add_argument('--footer', type=str, default='ขอบคุณที่ใช้บริการ', help='Footer text')
    
    args = parser.parse_args()
    
    # Parse items if provided
    items = []
    if args.items:
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
    output_path = create_custom_receipt(items, total, args.title, args.footer)
    if output_path:
        # Open Firefox with print settings
        open_firefox_with_print_settings(output_path)

if __name__ == "__main__":
    main()
