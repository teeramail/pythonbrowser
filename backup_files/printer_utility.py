#!/usr/bin/env python3
"""
Thermal Printer Utility - A simple utility for testing and configuring your thermal printer
"""

import sys
import os
from thermal_printer import get_printer, test_printer

def print_menu():
    """Print the main menu"""
    print("\nThermal Printer Utility")
    print("======================")
    print("1. Print test receipt (English)")
    print("2. Print test receipt (Thai)")
    print("3. Print custom text")
    print("4. Configure printer settings")
    print("5. Exit")
    print("\nEnter your choice (1-5): ", end="")

def print_test_receipt_english():
    """Print a test receipt in English"""
    print("\nPrinting test receipt in English...")
    printer = get_printer()
    if printer.connect():
        success = printer.print_receipt(
            "TEST RECEIPT",
            "Item 1........................$10.00\n"
            "Item 2........................$15.00\n"
            "Item 3........................$20.00\n"
            "---------------------------------\n"
            "Total.........................$45.00",
            "Thank you for your purchase!\nwww.example.com"
        )
        printer.disconnect()
        if success:
            print("Test receipt printed successfully!")
        else:
            print("Failed to print test receipt.")
    else:
        print("Failed to connect to printer.")

def print_test_receipt_thai():
    """Print a test receipt in Thai"""
    print("\nPrinting test receipt in Thai...")
    printer = get_printer()
    if printer.connect():
        success = printer.print_receipt(
            "ทดสอบการพิมพ์",  # "Print Test" in Thai
            "รายการที่ 1............฿100.00\n"
            "รายการที่ 2............฿150.00\n"
            "รายการที่ 3............฿200.00\n"
            "-----------------------\n"
            "รวม..................฿450.00",
            "ขอบคุณที่ใช้บริการ"  # "Thank you for your service" in Thai
        )
        printer.disconnect()
        if success:
            print("Thai test receipt printed successfully!")
        else:
            print("Failed to print Thai test receipt.")
    else:
        print("Failed to connect to printer.")

def print_custom_text():
    """Print custom text"""
    print("\nEnter your custom text (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if not line and lines and not lines[-1]:
            # Two consecutive empty lines
            if len(lines) > 0:
                lines.pop()  # Remove the last empty line
            break
        lines.append(line)
    
    text = "\n".join(lines)
    if not text.strip():
        print("No text entered. Returning to main menu.")
        return
    
    print("\nPrinting custom text...")
    printer = get_printer()
    if printer.connect():
        success = printer.print_text(text)
        printer.disconnect()
        if success:
            print("Custom text printed successfully!")
        else:
            print("Failed to print custom text.")
    else:
        print("Failed to connect to printer.")

def configure_printer():
    """Configure printer settings"""
    print("\nConfigure Printer Settings")
    print("=========================")
    
    # Check if printer_config.py exists
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "printer_config.py")
    if not os.path.exists(config_path):
        print("Creating default printer_config.py...")
        with open(config_path, "w") as f:
            f.write('''"""
Thermal Printer Configuration
Edit this file to customize your thermal printer settings
"""

# Thai character printing settings
# Choose the encoding that works best for your printer
# Options: 'tis-620', 'utf-8', 'cp874'
THAI_ENCODING = 'tis-620'

# Thai character code page
# 20 = Thai code page 42
# 21 = Thai code page 11
THAI_CODEPAGE = 20

# Thai character mode
# 49 = 3-pass mode (better quality, slower)
# 48 = 1-pass mode (lower quality, faster)
THAI_CHAR_MODE = 49

# Printer hardware settings
VENDOR_ID = 0x0483  # Xprinter USB Printer P
PRODUCT_ID = 0x070b  # Xprinter USB Printer P
''')
    
    # Read current configuration
    try:
        from printer_config import THAI_ENCODING, THAI_CODEPAGE, THAI_CHAR_MODE
        print(f"Current settings:")
        print(f"- Thai encoding: {THAI_ENCODING}")
        print(f"- Thai code page: {THAI_CODEPAGE}")
        print(f"- Thai character mode: {THAI_CHAR_MODE}")
    except ImportError:
        print("Could not import printer_config.py. Using default settings.")
        THAI_ENCODING = 'tis-620'
        THAI_CODEPAGE = 20
        THAI_CHAR_MODE = 49
    
    print("\nChoose setting to change:")
    print("1. Thai encoding")
    print("2. Thai code page")
    print("3. Thai character mode")
    print("4. Return to main menu")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == "1":
        print("\nChoose Thai encoding:")
        print("1. TIS-620 (Thai Industrial Standard)")
        print("2. UTF-8 (Unicode)")
        print("3. CP874 (Windows Thai)")
        
        encoding_choice = input("Enter your choice (1-3): ")
        if encoding_choice == "1":
            new_encoding = "tis-620"
        elif encoding_choice == "2":
            new_encoding = "utf-8"
        elif encoding_choice == "3":
            new_encoding = "cp874"
        else:
            print("Invalid choice. Keeping current setting.")
            return
        
        # Update configuration
        with open(config_path, "r") as f:
            config = f.read()
        
        config = config.replace(f"THAI_ENCODING = '{THAI_ENCODING}'", f"THAI_ENCODING = '{new_encoding}'")
        
        with open(config_path, "w") as f:
            f.write(config)
        
        print(f"Thai encoding updated to {new_encoding}.")
    
    elif choice == "2":
        print("\nChoose Thai code page:")
        print("1. Thai code page 42 (value 20)")
        print("2. Thai code page 11 (value 21)")
        
        codepage_choice = input("Enter your choice (1-2): ")
        if codepage_choice == "1":
            new_codepage = 20
        elif codepage_choice == "2":
            new_codepage = 21
        else:
            print("Invalid choice. Keeping current setting.")
            return
        
        # Update configuration
        with open(config_path, "r") as f:
            config = f.read()
        
        config = config.replace(f"THAI_CODEPAGE = {THAI_CODEPAGE}", f"THAI_CODEPAGE = {new_codepage}")
        
        with open(config_path, "w") as f:
            f.write(config)
        
        print(f"Thai code page updated to {new_codepage}.")
    
    elif choice == "3":
        print("\nChoose Thai character mode:")
        print("1. 3-pass mode (better quality, slower) (value 49)")
        print("2. 1-pass mode (lower quality, faster) (value 48)")
        
        mode_choice = input("Enter your choice (1-2): ")
        if mode_choice == "1":
            new_mode = 49
        elif mode_choice == "2":
            new_mode = 48
        else:
            print("Invalid choice. Keeping current setting.")
            return
        
        # Update configuration
        with open(config_path, "r") as f:
            config = f.read()
        
        config = config.replace(f"THAI_CHAR_MODE = {THAI_CHAR_MODE}", f"THAI_CHAR_MODE = {new_mode}")
        
        with open(config_path, "w") as f:
            f.write(config)
        
        print(f"Thai character mode updated to {new_mode}.")
    
    elif choice == "4":
        return
    
    else:
        print("Invalid choice. Returning to main menu.")

def main():
    """Main function"""
    while True:
        print_menu()
        choice = input()
        
        if choice == "1":
            print_test_receipt_english()
        elif choice == "2":
            print_test_receipt_thai()
        elif choice == "3":
            print_custom_text()
        elif choice == "4":
            configure_printer()
        elif choice == "5":
            print("\nExiting Thermal Printer Utility. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()
