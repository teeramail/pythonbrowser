from escpos.printer import Usb

# Vendor and Product IDs for your printer
VENDOR_ID = 0x0483
PRODUCT_ID = 0x070b

try:
    p = Usb(VENDOR_ID, PRODUCT_ID)
    p.text("Test Print\n")
    p.cut()
    print("Print sent successfully!")
except Exception as e:
    print("Error:", e)
