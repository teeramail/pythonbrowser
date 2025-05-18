#!/usr/bin/env python3
"""
Print Thai Receipt - Simple script to print Thai receipts from the kiosk browser
"""

import sys
import os
import argparse
from thai_image_printer import ThaiImagePrinter

def print_receipt(title, items_text, total, footer=None):
    """Print a Thai receipt with the given content"""
    printer = ThaiImagePrinter()
    
    if not printer.connect():
        print("Failed to connect to printer")
        return False
    
    try:
        # Build receipt text
        receipt_text = title + "\n\n"
        
        # Add items text
        receipt_text += items_text + "\n\n"
        
        # Add total
        receipt_text += f"รวม: {total}\n\n"
        
        # Add footer
        if footer:
            receipt_text += footer
        
        # Print the receipt
        # Use the CENTER alignment constant directly
        CENTER = [0x1B, 0x61, 0x01]  # ESC a 1
        printer.set_alignment(CENTER)
        printer.print_thai_text(receipt_text)
        printer.feed(1)
        printer.cut()
        
        print("Receipt printed successfully")
        return True
    
    except Exception as e:
        print(f"Error printing receipt: {e}")
        return False
    
    finally:
        printer.disconnect()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Print Thai Receipt')
    parser.add_argument('--title', type=str, default='ใบเสร็จรับเงิน', help='Receipt title')
    parser.add_argument('--items', type=str, required=True, help='Items text')
    parser.add_argument('--total', type=str, required=True, help='Total amount')
    parser.add_argument('--footer', type=str, default='ขอบคุณที่ใช้บริการ', help='Footer text')
    
    args = parser.parse_args()
    
    print_receipt(args.title, args.items, args.total, args.footer)

if __name__ == "__main__":
    main()
