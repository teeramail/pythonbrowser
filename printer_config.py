"""
Thermal Printer Configuration
Edit this file to customize your thermal printer settings
"""

# Thai character printing settings
# Choose the encoding that works best for your printer
# Options: 'tis-620', 'utf-8', 'cp874'
# Based on manufacturer specs, UTF-8 is recommended for Thai characters
THAI_ENCODING = 'utf-8'

# Thai character code page
# 20 = Thai code page 42
# 21 = Thai code page 11
# Based on manufacturer specs, Thai code page 11 works better for Thai characters
THAI_CODEPAGE = 21

# Thai character mode
# 49 = 3-pass mode (better quality, slower)
# 48 = 1-pass mode (lower quality, faster)
# 1-pass mode is recommended for thermal printers
THAI_CHAR_MODE = 48

# Printer hardware settings
VENDOR_ID = 0x0483  # Xprinter USB Printer P
PRODUCT_ID = 0x070b  # Xprinter USB Printer P
