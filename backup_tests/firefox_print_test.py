#!/usr/bin/env python3
"""
Firefox Print Test - Opens Firefox with a Thai test page for printing
"""

import os
import sys
import subprocess
import time
from urllib.parse import quote

def create_test_html():
    """Create a Thai test HTML file for Firefox to print"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Firefox Thai Print Test</title>
    <style>
        @page {
            size: 58mm 50mm;
            margin: 0;
        }
        @media print {
            body {
                width: 58mm;
                margin: 0;
                padding: 0;
            }
        }
        body {
            font-family: sans-serif;
            width: 58mm;
            margin: 0;
            padding: 0;
        }
        .receipt {
            width: 100%;
        }
        .header {
            text-align: center;
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 14pt;
        }
        .content {
            margin: 5px;
            font-size: 10pt;
        }
        .item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 3px;
        }
        .footer {
            text-align: center;
            font-size: 10pt;
            border-top: 1px dotted #000;
            padding-top: 3px;
            margin-top: 5px;
        }
        .print-button {
            display: block;
            margin: 10px auto;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14pt;
        }
        .instructions {
            margin: 10px;
            padding: 10px;
            border: 1px solid #ccc;
            background-color: #f9f9f9;
        }
        @media print {
            .instructions, .print-button {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="instructions">
        <h2>Firefox Thai Print Test</h2>
        <p>This page will test printing Thai characters to your 58mm thermal printer.</p>
        <p><strong>Print Settings:</strong></p>
        <ul>
            <li>Printer: ThermalPrinter</li>
            <li>Paper Size: Custom (58mm × 50mm)</li>
            <li>Margins: None</li>
            <li>Scale: 100%</li>
        </ul>
        <button class="print-button" onclick="window.print()">Print Test</button>
    </div>
    
    <div class="receipt">
        <div class="header">
            ทดสอบการพิมพ์ไทย
        </div>
        
        <div class="content">
            <div class="item">
                <span>วันที่:</span>
                <span>13/05/2025</span>
            </div>
            <div class="item">
                <span>เวลา:</span>
                <span>13:01</span>
            </div>
            
            <div class="item">
                <span>รายการ:</span>
                <span>กาแฟ</span>
            </div>
            <div class="item">
                <span>จำนวน:</span>
                <span>1</span>
            </div>
            <div class="item">
                <span>ราคา:</span>
                <span>฿45.00</span>
            </div>
            
            <div class="item">
                <span><strong>รวม:</strong></span>
                <span><strong>฿45.00</strong></span>
            </div>
        </div>
        
        <div class="footer">
            ขอบคุณที่ใช้บริการ
        </div>
    </div>
</body>
</html>
"""
    
    # Write the HTML content to a file
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firefox_thai_test.html')
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return test_file

def open_firefox_with_test_page():
    """Open Firefox with the Thai test page"""
    test_file = create_test_html()
    
    # Convert to file URL
    file_url = f"file://{test_file}"
    
    print(f"Opening Firefox with Thai test page: {file_url}")
    
    # Open Firefox with the test page
    subprocess.Popen(['firefox', file_url])
    
    print("Firefox opened with Thai test page")
    print("Please follow these steps to print:")
    print("1. Click the 'Print Test' button on the page")
    print("2. In the print dialog, select 'ThermalPrinter'")
    print("3. Click 'More settings' and set:")
    print("   - Paper size: Custom (58mm × 50mm)")
    print("   - Margins: None")
    print("   - Scale: 100%")
    print("4. Click 'Print' to send to your thermal printer")

if __name__ == "__main__":
    open_firefox_with_test_page()
