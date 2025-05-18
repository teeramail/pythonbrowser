#!/usr/bin/env python3
"""
Simple print test - This script tests printing to the thermal printer without sudo
"""

from thermal_printer import test_printer

print("Testing thermal printer without sudo...")
if test_printer():
    print("Success! The printer works without sudo.")
else:
    print("Failed to print. You may need to:")
    print("1. Unplug and replug the printer")
    print("2. Make sure the udev rules are properly installed")
    print("3. Try running with sudo if all else fails")
