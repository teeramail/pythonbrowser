#!/usr/bin/env python3
"""
Print HTML Receipt - Convert HTML to plain text and print to 58mm thermal printer
Uses the existing thermal_printer.py module for direct USB printing
"""

import sys
import os
import argparse
from bs4 import BeautifulSoup
from thermal_printer import ThermalPrinter

def html_to_text(html_content):
    """Convert HTML content to plain text for thermal printer"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get the title (first heading or title tag)
    title = ""
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text().strip()
    elif soup.title:
        title = soup.title.get_text().strip()
    
    # Extract text content
    text = soup.get_text().strip()
    
    # If we found a title, remove it from the content to avoid duplication
    if title and title in text:
        content = text.replace(title, "", 1).strip()
    else:
        content = text
        
    return title, content

def print_html_file(file_path):
    """Print an HTML file to the thermal printer"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        title, content = html_to_text(html_content)
        
        # Connect to the thermal printer
        printer = ThermalPrinter()
        
        # If no title was found, use a default
        if not title:
            title = "Receipt"
        
        # Add a footer
        footer = "Thank you!"
        
        # Print the receipt
        print(f"Printing receipt with title: {title}")
        print(f"Content length: {len(content)} characters")
        
        printer.print_receipt(title, content, footer)
        print("Receipt printed successfully!")
        return True
        
    except Exception as e:
        print(f"Error printing HTML file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Print HTML content to a 58mm thermal printer')
    parser.add_argument('html_file', help='HTML file to print')
    args = parser.parse_args()
    
    if not os.path.exists(args.html_file):
        print(f"Error: HTML file not found: {args.html_file}")
        return 1
    
    if print_html_file(args.html_file):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
