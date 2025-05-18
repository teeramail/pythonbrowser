#!/usr/bin/env python3
"""
Minimal Thai Print - Direct printing with minimal paper feed
"""

import sys
import usb.core
import usb.util
import time

# Printer constants
VENDOR_ID = 0x0483  # Xprinter USB Printer P
PRODUCT_ID = 0x070b  # Xprinter USB Printer P

# ESC/POS Commands
ESC = 0x1B  # Escape
GS = 0x1D   # Group Separator
FS = 0x1C   # Field Separator
LF = 0x0A   # Line Feed (new line)

# Thai code page
THAI_CODEPAGE = [ESC, 0x74, 0x15]  # Thai character code 11

# Initialize printer
INIT = [ESC, 0x40]

# Text formatting
CENTER = [ESC, 0x61, 0x01]  # Center alignment
LEFT = [ESC, 0x61, 0x00]    # Left alignment
BOLD_ON = [ESC, 0x45, 0x01]  # Bold on
BOLD_OFF = [ESC, 0x45, 0x00]  # Bold off

# Paper cut
CUT = [GS, 0x56, 0x00]  # Full cut

def connect_printer():
    """Connect to the thermal printer with minimal setup"""
    try:
        # Find the printer
        dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        
        if dev is None:
            print("Printer not found! Make sure it's connected and powered on.")
            return None
        
        # Detach kernel driver if active
        if dev.is_kernel_driver_active(0):
            try:
                dev.detach_kernel_driver(0)
                print("Kernel driver detached")
            except Exception as e:
                print(f"Error detaching kernel driver: {e}")
                return None
        
        # Set configuration
        try:
            dev.set_configuration()
            print("USB configuration set")
        except Exception as e:
            print(f"Error setting configuration: {e}")
            return None
        
        # Get endpoint
        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]
        
        ep_out = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: 
                usb.util.endpoint_direction(e.bEndpointAddress) == 
                usb.util.ENDPOINT_OUT
        )
        
        if ep_out is None:
            print("Could not find endpoint")
            return None
        
        print("Successfully connected to printer")
        return ep_out
    
    except Exception as e:
        print(f"Error connecting to printer: {e}")
        return None

def print_minimal_thai():
    """Print minimal Thai text with strict paper control"""
    ep_out = connect_printer()
    if not ep_out:
        return False
    
    try:
        # Initialize printer
        ep_out.write(bytes(INIT))
        
        # Set Thai code page
        ep_out.write(bytes(THAI_CODEPAGE))
        
        # Print header (centered, bold)
        ep_out.write(bytes(CENTER))
        ep_out.write(bytes(BOLD_ON))
        ep_out.write("Thai Test".encode('utf-8'))
        ep_out.write(bytes([LF]))
        ep_out.write(bytes(BOLD_OFF))
        
        # Print Thai text (left-aligned)
        ep_out.write(bytes(LEFT))
        
        # Thai text - using UTF-8 encoding
        thai_text = "สวัสดี"
        ep_out.write(thai_text.encode('utf-8'))
        ep_out.write(bytes([LF]))
        
        # Cut paper immediately without extra feeds
        ep_out.write(bytes(CUT))
        
        print("Minimal Thai text printed successfully")
        return True
        
    except Exception as e:
        print(f"Error printing: {e}")
        return False

if __name__ == "__main__":
    print("Starting minimal Thai print test...")
    if print_minimal_thai():
        print("Test completed successfully")
    else:
        print("Test failed")
