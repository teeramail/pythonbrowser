#!/usr/bin/env python3
"""
Thai Encoding Test - Tests different encoding and code page settings
for printing Thai characters on a 58mm thermal printer
"""

import sys
import time
from thermal_printer import ThermalPrinter, CODEPAGE_THAI42, CODEPAGE_THAI11
from thermal_printer import THAI_CHARACTER_MODE_3PASS, THAI_CHARACTER_MODE_1PASS

def test_thai_printing():
    """Test different Thai encoding and code page combinations"""
    printer = ThermalPrinter()
    
    if not printer.connect():
        print("Failed to connect to printer")
        return False
    
    # Thai test text
    thai_title = "ทดสอบภาษาไทย"
    thai_content = (
        "รายการ: กาแฟ\n"
        "จำนวน: 1\n"
        "ราคา: ฿45.00\n"
        "รวม: ฿45.00\n"
        "ขอบคุณที่ใช้บริการ"
    )
    
    # Test combinations
    combinations = [
        {
            "name": "UTF-8 + Thai 42 + 3-pass",
            "encoding": "utf-8",
            "codepage": CODEPAGE_THAI42,
            "charmode": THAI_CHARACTER_MODE_3PASS
        },
        {
            "name": "UTF-8 + Thai 11 + 3-pass",
            "encoding": "utf-8",
            "codepage": CODEPAGE_THAI11,
            "charmode": THAI_CHARACTER_MODE_3PASS
        },
        {
            "name": "UTF-8 + Thai 42 + 1-pass",
            "encoding": "utf-8",
            "codepage": CODEPAGE_THAI42,
            "charmode": THAI_CHARACTER_MODE_1PASS
        },
        {
            "name": "UTF-8 + Thai 11 + 1-pass",
            "encoding": "utf-8",
            "codepage": CODEPAGE_THAI11,
            "charmode": THAI_CHARACTER_MODE_1PASS
        },
        {
            "name": "TIS-620 + Thai 42 + 3-pass",
            "encoding": "tis-620",
            "codepage": CODEPAGE_THAI42,
            "charmode": THAI_CHARACTER_MODE_3PASS
        },
        {
            "name": "TIS-620 + Thai 11 + 3-pass",
            "encoding": "tis-620",
            "codepage": CODEPAGE_THAI11,
            "charmode": THAI_CHARACTER_MODE_3PASS
        }
    ]
    
    for combo in combinations:
        print(f"\nTesting: {combo['name']}")
        
        # Initialize printer
        printer.ep_out.write(bytes([0x1B, 0x40]))  # ESC @ - Initialize printer
        
        # Set character mode
        printer.ep_out.write(bytes(combo["charmode"]))
        
        # Set code page
        printer.ep_out.write(bytes(combo["codepage"]))
        
        # Print test header
        printer.ep_out.write(bytes([0x1B, 0x61, 0x01]))  # Center alignment
        printer.ep_out.write(bytes([0x1B, 0x45, 0x01]))  # Bold on
        printer.ep_out.write(f"Test: {combo['name']}".encode('ascii', errors='replace'))
        printer.ep_out.write(bytes([0x0A]))  # Line feed
        
        # Print Thai title
        try:
            printer.ep_out.write(thai_title.encode(combo["encoding"], errors='replace'))
            printer.ep_out.write(bytes([0x0A]))  # Line feed
        except Exception as e:
            print(f"Error encoding title: {e}")
        
        # Print Thai content
        printer.ep_out.write(bytes([0x1B, 0x61, 0x00]))  # Left alignment
        printer.ep_out.write(bytes([0x1B, 0x45, 0x00]))  # Bold off
        try:
            printer.ep_out.write(thai_content.encode(combo["encoding"], errors='replace'))
            printer.ep_out.write(bytes([0x0A, 0x0A]))  # Line feeds
        except Exception as e:
            print(f"Error encoding content: {e}")
        
        # Feed and cut
        printer.ep_out.write(bytes([0x1D, 0x56, 0x00]))  # Cut paper
        
        # Wait between tests
        time.sleep(2)
    
    printer.disconnect()
    return True

if __name__ == "__main__":
    print("Starting Thai encoding test...")
    if test_thai_printing():
        print("Test completed successfully")
    else:
        print("Test failed")
