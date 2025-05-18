#!/usr/bin/env python3
"""
Create Firefox Thermal Profile - Creates a Firefox profile with custom print settings for 58mm thermal printer
"""

import os
import sys
import subprocess
import time
import json
import shutil
from pathlib import Path

def create_firefox_thermal_profile():
    """Create a Firefox profile with custom print settings for 58mm thermal printer"""
    try:
        # Get Firefox profiles directory
        home_dir = str(Path.home())
        firefox_profiles_dir = os.path.join(home_dir, ".mozilla", "firefox")
        
        if not os.path.exists(firefox_profiles_dir):
            print(f"Firefox profiles directory not found: {firefox_profiles_dir}")
            return False
        
        # Create a new Firefox profile named "thermal"
        print("Creating Firefox thermal profile...")
        cmd = ["firefox", "-CreateProfile", "thermal"]
        subprocess.run(cmd, check=True)
        
        # Find the newly created profile directory
        profiles_ini_path = os.path.join(firefox_profiles_dir, "profiles.ini")
        
        if not os.path.exists(profiles_ini_path):
            print(f"Firefox profiles.ini not found: {profiles_ini_path}")
            return False
        
        # Parse profiles.ini to find the thermal profile path
        thermal_profile_path = None
        with open(profiles_ini_path, 'r') as f:
            lines = f.readlines()
            
            in_thermal_section = False
            for line in lines:
                line = line.strip()
                
                if line == "[Profile1]" or line.startswith("[Profile"):
                    in_thermal_section = False
                
                if "Name=thermal" in line:
                    in_thermal_section = True
                
                if in_thermal_section and line.startswith("Path="):
                    thermal_profile_path = line.split("=")[1]
        
        if not thermal_profile_path:
            print("Could not find thermal profile path")
            return False
        
        # Get full path to thermal profile
        thermal_profile_full_path = os.path.join(firefox_profiles_dir, thermal_profile_path)
        
        if not os.path.exists(thermal_profile_full_path):
            print(f"Thermal profile directory not found: {thermal_profile_full_path}")
            return False
        
        print(f"Thermal profile created at: {thermal_profile_full_path}")
        
        # Create prefs.js with custom print settings if it doesn't exist
        prefs_path = os.path.join(thermal_profile_full_path, "prefs.js")
        
        # Custom print settings for 58mm thermal printer
        print_settings = [
            # Paper size (58mm x 100mm)
            'user_pref("print.printer_ThermalPOS.print_paper_size", 0);',  # 0 = custom size
            'user_pref("print.printer_ThermalPOS.print_paper_width", "58.00");',  # Width in mm
            'user_pref("print.printer_ThermalPOS.print_paper_height", "100.00");',  # Height in mm
            
            # Margins (minimum)
            'user_pref("print.printer_ThermalPOS.print_margin_top", "0.00");',
            'user_pref("print.printer_ThermalPOS.print_margin_bottom", "0.00");',
            'user_pref("print.printer_ThermalPOS.print_margin_left", "0.00");',
            'user_pref("print.printer_ThermalPOS.print_margin_right", "0.00");',
            
            # Scaling (100%)
            'user_pref("print.printer_ThermalPOS.print_scaling", "1.00");',
            
            # Print background (enabled)
            'user_pref("print.printer_ThermalPOS.print_bgcolor", true);',
            'user_pref("print.printer_ThermalPOS.print_bgimages", true);',
            
            # Print headers and footers (disabled)
            'user_pref("print.printer_ThermalPOS.print_headerleft", "");',
            'user_pref("print.printer_ThermalPOS.print_headercenter", "");',
            'user_pref("print.printer_ThermalPOS.print_headerright", "");',
            'user_pref("print.printer_ThermalPOS.print_footerleft", "");',
            'user_pref("print.printer_ThermalPOS.print_footercenter", "");',
            'user_pref("print.printer_ThermalPOS.print_footerright", "");',
            
            # Default printer
            'user_pref("print.printer_ThermalPOS.print_in_color", false);',  # Black and white
            'user_pref("print.printer_ThermalPOS.print_orientation", 0);',  # 0 = portrait
            'user_pref("print.printer_ThermalPOS.print_page_delay", 50);',  # Page delay in ms
            'user_pref("print.printer_ThermalPOS.print_resolution", 0);',  # 0 = default resolution
            'user_pref("print.printer_ThermalPOS.print_to_file", false);',  # Don't print to file
            'user_pref("print.printer_ThermalPOS.print_unwriteable_margin_bottom", 0);',
            'user_pref("print.printer_ThermalPOS.print_unwriteable_margin_left", 0);',
            'user_pref("print.printer_ThermalPOS.print_unwriteable_margin_right", 0);',
            'user_pref("print.printer_ThermalPOS.print_unwriteable_margin_top", 0);',
            
            # Set ThermalPOS as default printer
            'user_pref("print.printer_list", "ThermalPOS");',
            'user_pref("print.printer", "ThermalPOS");',
            
            # Auto-print without dialog
            'user_pref("print.always_print_silent", true);',
            'user_pref("print.show_print_progress", false);'
        ]
        
        # Append custom print settings to prefs.js
        with open(prefs_path, 'a') as f:
            f.write("\n// Custom print settings for 58mm thermal printer\n")
            for setting in print_settings:
                f.write(setting + "\n")
        
        print("Custom print settings added to thermal profile")
        
        # Create a script to launch Firefox with the thermal profile
        launch_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launch_firefox_thermal.sh")
        
        with open(launch_script_path, 'w') as f:
            f.write("#!/bin/bash\n\n")
            f.write("# Launch Firefox with thermal profile\n")
            f.write(f'firefox -P "thermal" "$@"\n')
        
        # Make the launch script executable
        os.chmod(launch_script_path, 0o755)
        
        print(f"Launch script created at: {launch_script_path}")
        print("\nTo use the thermal profile, run:")
        print(f"  {launch_script_path} [URL]")
        
        return True
    
    except Exception as e:
        print(f"Error creating Firefox thermal profile: {e}")
        return False

def main():
    """Main function"""
    create_firefox_thermal_profile()

if __name__ == "__main__":
    main()
