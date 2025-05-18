#!/usr/bin/env python3
import usb.core
import usb.util
import time

# Xprinter USB Printer P (Vendor ID: 0483, Product ID: 070b)
VENDOR_ID = 0x0483
PRODUCT_ID = 0x070b

# ESC/POS Commands
ESC = 0x1B  # Escape
GS = 0x1D   # Group Separator
INIT = [ESC, 0x40]  # Initialize printer
LINE_FEED = [0x0A]  # Line feed
CUT = [GS, 0x56, 0x00]  # Full cut

def main():
    # Find the printer
    print("Looking for printer...")
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    
    if dev is None:
        print("Printer not found!")
        return
    
    print(f"Printer found: {dev}")
    
    # Detach kernel driver if active
    if dev.is_kernel_driver_active(0):
        try:
            dev.detach_kernel_driver(0)
            print("Kernel driver detached")
        except Exception as e:
            print(f"Error detaching kernel driver: {e}")
    
    # Set configuration
    try:
        dev.set_configuration()
        print("Configuration set")
    except Exception as e:
        print(f"Error setting configuration: {e}")
        return
    
    # Get endpoint
    cfg = dev.get_active_configuration()
    interface = cfg[(0,0)]
    
    ep_out = usb.util.find_descriptor(
        interface,
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
    )
    
    if ep_out is None:
        print("Output endpoint not found!")
        return
    
    print(f"Output endpoint found: {ep_out}")
    
    # Initialize printer
    try:
        ep_out.write(bytes(INIT))
        print("Printer initialized")
        
        # Print test message
        test_message = "Test Print\n58mm Thermal Printer\nXprinter Model\n\n\n"
        ep_out.write(test_message.encode('ascii'))
        ep_out.write(bytes(LINE_FEED))
        ep_out.write(bytes(LINE_FEED))
        ep_out.write(bytes(LINE_FEED))
        
        # Cut paper
        ep_out.write(bytes(CUT))
        
        print("Test message sent to printer")
    except Exception as e:
        print(f"Error communicating with printer: {e}")
    
    # Release the device
    usb.util.dispose_resources(dev)
    print("Device resources released")

if __name__ == "__main__":
    main()
