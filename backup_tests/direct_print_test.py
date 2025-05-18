#!/usr/bin/env python3
"""
Direct print test - This script directly prints to the thermal printer
without involving the browser.
"""

import sys
import os
from datetime import datetime

# Import our thermal printer module
try:
    from thermal_printer import get_printer, test_printer
    DIRECT_THERMAL_PRINTING = True
except ImportError:
    print("Thermal printer module not found")
    DIRECT_THERMAL_PRINTING = False

def print_sample_receipt():
    """Print a sample receipt to the thermal printer"""
    if not DIRECT_THERMAL_PRINTING:
        print("Thermal printer module not available")
        return False
    
    print("Starting direct print test...")
    
    # Create sample receipt content
    title = "SAMPLE RECEIPT"
    content = (
        "Item 1........................$10.00\n"
        "Item 2........................$15.00\n"
        "Item 3........................$20.00\n"
        "---------------------------------\n"
        "Total.........................$45.00"
    )
    
    # Current date/time for the receipt
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer = f"Printed: {current_time}\nThank you for your purchase!"
    
    # Try direct USB printing
    try:
        print("Attempting direct USB printing...")
        
        # First run a test print to make sure the printer is working
        print("Running test print...")
        if test_printer():
            print("Test print successful, proceeding with actual print...")
            
            # Now print the actual content
            printer = get_printer()
            if printer.connect():
                success = printer.print_receipt(title, content, footer)
                printer.disconnect()
                if success:
                    print("Receipt printed successfully using direct USB")
                    return True
                else:
                    print("Failed to print receipt using direct USB")
            else:
                print("Failed to connect to thermal printer")
        else:
            print("Test print failed, cannot proceed with direct USB printing")
    except Exception as e:
        print(f"Error using thermal printer: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def main():
    """Main function"""
    print("Direct Print Test")
    print("-----------------")
    
    # Print sample receipt
    if print_sample_receipt():
        print("Sample receipt printed successfully!")
    else:
        print("Failed to print sample receipt")
    
    # Also try CUPS printing as a fallback
    try:
        print("\nTrying CUPS printing as fallback...")
        # Create a test file
        temp_file = "/tmp/cups_test.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("CUPS TEST PRINT\n\n")
            f.write("This is a test print from CUPS\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Try to print using CUPS
        printer_name = "XprinterThermal"  # Make sure this matches your CUPS printer name
        print(f"Sending to CUPS printer: {printer_name}")
        result = os.system(f"lp -d {printer_name} {temp_file}")
        print(f"CUPS command result: {result}")
        
        if result == 0:
            print(f"Test print sent to {printer_name} printer via CUPS")
        else:
            print(f"Failed to send test print to {printer_name} printer via CUPS")
    except Exception as e:
        print(f"Error with CUPS printing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
