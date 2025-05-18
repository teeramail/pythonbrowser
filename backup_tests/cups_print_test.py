#!/usr/bin/env python3
"""
CUPS Print Test - Tests printing to the thermal printer using CUPS
"""

import os
import sys
import subprocess
import time

def print_test_page(html_file):
    """Print an HTML file to the thermal printer using CUPS"""
    print(f"Printing {html_file} to ThermalPOS printer...")
    
    # Get the absolute path to the HTML file
    file_path = os.path.abspath(html_file)
    
    # Use lp command to print the file
    cmd = ["lp", "-d", "ThermalPOS", "-o", "media=Custom.58x50mm", 
           "-o", "page-left=0", "-o", "page-right=0", 
           "-o", "page-top=0", "-o", "page-bottom=0",
           "-o", "fit-to-page", file_path]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print(f"Print job submitted successfully: {stdout.decode().strip()}")
            return True
        else:
            print(f"Error printing: {stderr.decode().strip()}")
            return False
    except Exception as e:
        print(f"Exception while printing: {e}")
        return False

def main():
    """Test printing with the generic POS driver"""
    # First test with English content
    english_test = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generic_pos_test.html')
    if os.path.exists(english_test):
        print("\nTesting with English content...")
        print_test_page(english_test)
        time.sleep(5)  # Wait for printing to complete
    else:
        print(f"Error: Test file not found: {english_test}")
    
    # Then test with Thai content
    thai_test = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generic_pos_thai_test.html')
    if os.path.exists(thai_test):
        print("\nTesting with Thai content...")
        print_test_page(thai_test)
    else:
        print(f"Error: Test file not found: {thai_test}")

if __name__ == "__main__":
    main()
