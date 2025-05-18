#!/usr/bin/env python3
"""
Thai Encoding Test - This script tests different encoding options for Thai characters
"""

import sys
from thermal_printer import ThermalPrinter, INIT, LINE_FEED, CUT
from thermal_printer import CODEPAGE_PC437, CODEPAGE_THAI42, CODEPAGE_THAI11
from thermal_printer import THAI_CHARACTER_MODE_3PASS, THAI_CHARACTER_MODE_1PASS

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

def test_encoding(encoding_name, codepage, char_mode, encoding):
    """Test a specific encoding and code page"""
    print(f"\nTesting {encoding_name} encoding with code page {codepage[2]} and character mode {char_mode[2]}...")
    
    printer = ThermalPrinter()
    if printer.connect():
        try:
            # Initialize printer
            printer.ep_out.write(bytes(INIT))
            
            # Set character mode
            printer.ep_out.write(bytes(char_mode))
            
            # Set code page
            printer.ep_out.write(bytes(codepage))
            
            # Print header
            printer.ep_out.write(f"=== {encoding_name} ===\n".encode('ascii', errors='replace'))
            
            # Print Thai text with the specified encoding
            try:
                printer.ep_out.write(thai_title.encode(encoding, errors='replace'))
                printer.ep_out.write(bytes(LINE_FEED))
                printer.ep_out.write(bytes(LINE_FEED))
                printer.ep_out.write(thai_content.encode(encoding, errors='replace'))
                printer.ep_out.write(bytes(LINE_FEED))
                printer.ep_out.write(thai_footer.encode(encoding, errors='replace'))
                printer.ep_out.write(bytes(LINE_FEED))
                printer.ep_out.write(bytes(LINE_FEED))
                
                # Add separator
                printer.ep_out.write("===================\n".encode('ascii', errors='replace'))
                printer.ep_out.write(bytes(LINE_FEED))
                
                success = True
            except Exception as e:
                print(f"Error encoding with {encoding}: {e}")
                success = False
            
            printer.disconnect()
            return success
        except Exception as e:
            print(f"Error during printing: {e}")
            printer.disconnect()
            return False
    else:
        print("Failed to connect to printer")
        return False

def main():
    """Test different encoding options"""
    print("Thai Encoding Test")
    print("=================")
    
    # Test different combinations of encodings and code pages
    tests = [
        # (Name, Code Page, Character Mode, Encoding)
        ("TIS-620", CODEPAGE_THAI42, THAI_CHARACTER_MODE_3PASS, "tis-620"),
        ("UTF-8", CODEPAGE_THAI42, THAI_CHARACTER_MODE_3PASS, "utf-8"),
        ("CP874", CODEPAGE_THAI42, THAI_CHARACTER_MODE_3PASS, "cp874"),
        ("TIS-620", CODEPAGE_THAI11, THAI_CHARACTER_MODE_3PASS, "tis-620"),
        ("UTF-8", CODEPAGE_THAI11, THAI_CHARACTER_MODE_3PASS, "utf-8"),
        ("CP874", CODEPAGE_THAI11, THAI_CHARACTER_MODE_3PASS, "cp874"),
        ("TIS-620", CODEPAGE_THAI42, THAI_CHARACTER_MODE_1PASS, "tis-620"),
        ("UTF-8", CODEPAGE_THAI42, THAI_CHARACTER_MODE_1PASS, "utf-8"),
        ("CP874", CODEPAGE_THAI42, THAI_CHARACTER_MODE_1PASS, "cp874"),
    ]
    
    # Run the tests
    results = []
    for name, codepage, char_mode, encoding in tests:
        try:
            success = test_encoding(name, codepage, char_mode, encoding)
            results.append((name, codepage[2], char_mode[2], encoding, success))
        except LookupError:
            print(f"Encoding {encoding} not available, skipping")
            results.append((name, codepage[2], char_mode[2], encoding, False))
    
    # Print summary
    print("\nTest Results:")
    print("=============")
    for name, codepage, char_mode, encoding, success in results:
        status = "SUCCESS" if success else "FAILED"
        print(f"{name} with code page {codepage} and mode {char_mode}: {status}")
    
    print("\nPlease check the printed output to see which encoding looks best for Thai characters.")
    print("The best option will have correct Thai characters without missing or incorrect symbols.")

if __name__ == "__main__":
    main()
