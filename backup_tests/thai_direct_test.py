#!/usr/bin/env python3
"""
Thai Direct Test - Tests printing Thai characters directly to the thermal printer
using the manufacturer's recommended settings
"""

import sys
from thermal_printer import ThermalPrinter

def test_thai_printing():
    """Test Thai character printing with manufacturer's recommended settings"""
    print("Starting Thai direct printing test...")
    
    # Connect to the printer
    printer = ThermalPrinter()
    if not printer.connect():
        print("Failed to connect to printer")
        return False
    
    # Thai test receipt
    title = "ทดสอบภาษาไทย"
    content = (
        "รายการสินค้า:\n"
        "กาแฟ........................฿45.00\n"
        "ชาเขียว......................฿40.00\n"
        "น้ำส้ม........................฿35.00\n"
        "--------------------------------\n"
        "รวมทั้งสิ้น....................฿120.00\n"
    )
    footer = "ขอบคุณที่ใช้บริการ"
    
    # Print the receipt
    print(f"Printing Thai receipt with title: {title}")
    success = printer.print_receipt(title, content, footer)
    
    if success:
        print("Thai receipt printed successfully!")
    else:
        print("Failed to print Thai receipt")
    
    printer.disconnect()
    return success

if __name__ == "__main__":
    if test_thai_printing():
        print("Test completed successfully")
    else:
        print("Test failed")
