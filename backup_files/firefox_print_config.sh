#!/bin/bash

# Create Firefox printing preferences for thermal printer
FIREFOX_PREFS_DIR="$HOME/.mozilla/firefox"
PROFILE_DIR=$(find "$FIREFOX_PREFS_DIR" -name "*.default*" | head -n 1)

if [ -z "$PROFILE_DIR" ]; then
    echo "Firefox profile directory not found."
    exit 1
fi

# Create or update user.js file with thermal printer settings
cat >> "$PROFILE_DIR/user.js" << EOF
// Thermal printer settings
user_pref("print.print_paper_height", "50");
user_pref("print.print_paper_width", "58");
user_pref("print.print_paper_size_unit", 1);  // 1 = mm
user_pref("print.print_margin_bottom", "0");
user_pref("print.print_margin_left", "0");
user_pref("print.print_margin_right", "0");
user_pref("print.print_margin_top", "0");
user_pref("print.print_scaling", "1.0");
user_pref("print.print_shrink_to_fit", false);
user_pref("print.print_to_filename", "");
user_pref("print.printer_ThermalPrinter.print_bg_colors", true);
user_pref("print.printer_ThermalPrinter.print_bg_images", true);
user_pref("print.printer_ThermalPrinter.print_downloadfonts", true);
user_pref("print.printer_ThermalPrinter.print_duplex", 0);
user_pref("print.printer_ThermalPrinter.print_edge_bottom", 0);
user_pref("print.printer_ThermalPrinter.print_edge_left", 0);
user_pref("print.printer_ThermalPrinter.print_edge_right", 0);
user_pref("print.printer_ThermalPrinter.print_edge_top", 0);
user_pref("print.printer_ThermalPrinter.print_evenpages", true);
user_pref("print.printer_ThermalPrinter.print_footerleft", "");
user_pref("print.printer_ThermalPrinter.print_footerright", "");
user_pref("print.printer_ThermalPrinter.print_headerleft", "");
user_pref("print.printer_ThermalPrinter.print_headerright", "");
user_pref("print.printer_ThermalPrinter.print_in_color", true);
user_pref("print.printer_ThermalPrinter.print_margin_bottom", "0");
user_pref("print.printer_ThermalPrinter.print_margin_left", "0");
user_pref("print.printer_ThermalPrinter.print_margin_right", "0");
user_pref("print.printer_ThermalPrinter.print_margin_top", "0");
user_pref("print.printer_ThermalPrinter.print_oddpages", true);
user_pref("print.printer_ThermalPrinter.print_orientation", 0);
user_pref("print.printer_ThermalPrinter.print_page_delay", 50);
user_pref("print.printer_ThermalPrinter.print_paper_height", "50");
user_pref("print.printer_ThermalPrinter.print_paper_size_unit", 1);
user_pref("print.printer_ThermalPrinter.print_paper_width", "58");
user_pref("print.printer_ThermalPrinter.print_resolution", "203");
user_pref("print.printer_ThermalPrinter.print_reversed", false);
user_pref("print.printer_ThermalPrinter.print_scaling", "1.0");
user_pref("print.printer_ThermalPrinter.print_shrink_to_fit", false);
user_pref("print.printer_ThermalPrinter.print_to_file", false);
user_pref("print.printer_ThermalPrinter.print_unwriteable_margin_bottom", 0);
user_pref("print.printer_ThermalPrinter.print_unwriteable_margin_left", 0);
user_pref("print.printer_ThermalPrinter.print_unwriteable_margin_right", 0);
user_pref("print.printer_ThermalPrinter.print_unwriteable_margin_top", 0);
EOF

echo "Firefox thermal printer settings have been configured."
echo "Please restart Firefox for the changes to take effect."
