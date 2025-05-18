#!/usr/bin/env python3
"""
Kiosk Browser - A full-screen browser for kiosk machines running on Windows or Linux
Features:
- Automatically loads a specified website
- Supports autoplay of sound
- Auto-print functionality
- Runs in fullscreen kiosk mode
"""

import sys
import os
import platform
import subprocess
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtGui import QKeySequence
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

# Import the digit image generator
try:
    from digit_images import create_number_image
    CUSTOM_DIGIT_RENDERING = True
    print("Custom digit rendering available")
except ImportError:
    print("Custom digit rendering not available, using fonts instead")
    CUSTOM_DIGIT_RENDERING = False

# Import our thermal printer module and PIL for image rendering
try:
    from thermal_printer import get_printer
    from PIL import Image, ImageDraw, ImageFont
    from thai_receipt import ThaiReceiptGenerator
    import tempfile
    import os
    DIRECT_THERMAL_PRINTING = True
    print("Thermal printer module loaded successfully")
except ImportError as e:
    print(f"Thermal printer module or PIL not found: {e}, falling back to CUPS printing")
    DIRECT_THERMAL_PRINTING = False

# Import configuration
try:
    from kiosk_config import *
except ImportError:
    # Default configuration if config file is missing
    DEFAULT_URL = "https://example.com"
    AUTO_PRINT_INTERVAL = 3600000
    AUTO_PRINT_ENABLED = True
    ENABLE_AUTOPLAY = True
    KIOSK_MODE = True
    BROWSER_WIDTH = 1280
    BROWSER_HEIGHT = 800
    DEV_MODE = True
    EXIT_SHORTCUT_ENABLED = True

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

class WebEngineUrlInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts URL requests to modify headers for autoplay support"""
    def interceptRequest(self, info):
        # Add headers to enable autoplay
        info.setHttpHeader(b"Autoplay-Policy", b"no-user-gesture-required")

class KioskBrowser(QMainWindow):
    def __init__(self, url=DEFAULT_URL):
        super().__init__()
        self.init_ui()
        self.load_url(url)
        if AUTO_PRINT_ENABLED:
            self.setup_auto_print()
        
        # Initialize Thai receipt generator
        if DIRECT_THERMAL_PRINTING:
            try:
                self.thai_receipt_generator = ThaiReceiptGenerator()
                print("Thai receipt generator initialized")
            except Exception as e:
                print(f"Error initializing Thai receipt generator: {e}")
                self.thai_receipt_generator = None
        
    def init_ui(self):
        # Create web view
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        
        # Configure web settings
        settings = self.web_view.settings()
        
        # Enable autoplay
        if ENABLE_AUTOPLAY:
            settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
            settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        
        # Set up kiosk mode
        if KIOSK_MODE:
            self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            self.showFullScreen()
            
            # Set up keyboard shortcuts
            if EXIT_SHORTCUT_ENABLED:
                self.exit_shortcut = QShortcut(QKeySequence("Ctrl+Alt+Q"), self)
                self.exit_shortcut.activated.connect(self.close)
                
            # Add print shortcut (P key)
            self.print_shortcut = QShortcut(QKeySequence("P"), self)
            self.print_shortcut.activated.connect(self.print_page)
            print("Press 'P' to print a receipt")
        else:
            # If not in kiosk mode, set a reasonable window size
            self.resize(BROWSER_WIDTH, BROWSER_HEIGHT)
        
        self.setWindowTitle("Kiosk Browser")
        
    def load_url(self, url):
        """Load the specified URL"""
        self.web_view.load(QUrl(url))
        
    def setup_auto_print(self):
        """Set up auto-print functionality"""
        if AUTO_PRINT_INTERVAL > 0:
            print(f"Setting up auto-print with interval: {AUTO_PRINT_INTERVAL}ms")
            self.print_timer = QTimer(self)
            self.print_timer.timeout.connect(self.print_page)
            self.print_timer.start(AUTO_PRINT_INTERVAL)
            
        # Add JavaScript bridge to enable printing from JavaScript
        print("Setting up JavaScript print bridge...")
        js_bridge_code = """
        // Monitor button clicks for printing
        document.addEventListener('click', function(event) {
            if (event.target.tagName === 'BUTTON' || 
                event.target.closest('button') || 
                event.target.classList.contains('v-btn') || 
                event.target.closest('.v-btn')) {
                const buttonText = event.target.textContent || 
                                   (event.target.closest('button') ? event.target.closest('button').textContent : '') ||
                                   (event.target.closest('.v-btn') ? event.target.closest('.v-btn').textContent : '');
                if (buttonText.includes('กดเรียกคิว') || buttonText.includes('เรียกคิว')) {
                    console.log('QUEUE_BUTTON_CLICKED');
                    setTimeout(function() {
                        window.printReceipt();
                    }, 1000);
                }
            }
        });
        
        // Monitor API calls to detect when a queue number is updated
        const originalFetch = window.fetch;
        window.fetch = function() {
            const promise = originalFetch.apply(this, arguments);
            
            // Check if this is a call to the queue API
            if (arguments[0] && arguments[0].includes('regisshow')) {
                promise.then(function() {
                    console.log('QUEUE_API_CALLED');
                    
                    // Wait for the response to be processed and UI to update
                    setTimeout(function() {
                        window.printReceipt();
                    }, 2500);  // Increased to 2.5 seconds for better reliability
                });
            }
            
            return promise;
        };
        
        // Override axios for API monitoring
        if (window.axios) {
            const originalPut = window.axios.put;
            window.axios.put = function() {
                const promise = originalPut.apply(this, arguments);
                
                // Check if this is a call to the queue API
                if (arguments[0] && arguments[0].includes('regisshow')) {
                    console.log('QUEUE_API_CALLED_AXIOS');
                    
                    // Wait for the response to be processed and UI to update
                    setTimeout(function() {
                        window.printReceipt();
                    }, 2500);  // Increased to 2.5 seconds for better reliability
                }
                
                return promise;
            };
        }
        
        // Add a global function that can be called from any page
        window.printReceipt = function() {
            console.log('PRINT_REQUESTED');
        };
        
        console.log('Queue print bridge installed');
        """
        self.web_view.page().loadFinished.connect(lambda ok: self.web_view.page().runJavaScript(js_bridge_code))
        
        # Connect JavaScript print events to our silent print function
        self.web_view.page().printRequested.connect(self.print_page)
        
        # Set up a JavaScript console message handler
        # Different PyQt5 versions have different methods for this
        try:
            # Try the newer method first
            self.web_view.page().javaScriptConsoleMessageReceived.connect(self.handle_console_message)
            print("Connected to javaScriptConsoleMessageReceived signal")
        except AttributeError:
            # Fall back to the older method
            try:
                # Connect to the older signal if available
                self.web_view.page().javaScriptConsoleMessage = self.handle_console_message_old
                print("Using older javaScriptConsoleMessage method")
            except Exception as e:
                print(f"Could not set up console message handler: {e}")
                print("JavaScript print detection via console may not work")
    
    def print_page(self):
        """Print the current page silently to the POS printer"""
        print("Print page method called - attempting to print...")
        
        def extract_queue_info(html_content):
            """Extract queue information from the HTML content"""
            # This function extracts queue data from the page, including number, date, and waiting count
            import re
            import json
            
            # Print debug info about the HTML content
            print(f"HTML Content length: {len(html_content)}")
            print(f"HTML Content preview: {html_content[:200]}...")
            
            # Result dictionary to return
            result = {
                'queue_number': "0",
                'timestamp': "",
                'waiting_count': 0  # Default to 0
            }
            
            # Look for a large number in the center of the page (likely the queue number)
            # First try to find the numbershow in Vue.js data
            queue_match = re.search(r'numbershow[^:]*:[^"]*"(\d+)"', html_content)
            if queue_match:
                result['queue_number'] = queue_match.group(1)
                print(f"Found queue number from numbershow: {result['queue_number']}")
            else:
                # Then try to find a number between 1-999 that's surrounded by whitespace
                queue_match = re.search(r'\s(\d{1,3})\s', html_content)
                if queue_match:
                    result['queue_number'] = queue_match.group(1)
                    print(f"Found queue number from whitespace pattern: {result['queue_number']}")
                else:
                    # If that fails, look for any number
                    queue_match = re.search(r'\b(\d{1,3})\b', html_content)
                    if queue_match:
                        result['queue_number'] = queue_match.group(1)
                        print(f"Found queue number from word boundary pattern: {result['queue_number']}")
            
            # Extract date/time - looking for date format like "16/05/ 05:12"
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\s*\d{1,2}:\d{1,2})', html_content)
            if date_match:
                result['timestamp'] = date_match.group(1)
            
            # Extract waiting count from the Vue.js app html content
            # PRIORITY 1: Look for Thai format "รอXคิว" which is the rendered content
            try:
                # First check for the Thai wait text which is most accurate
                waiting_match = re.search(r'รอ(\d+)คิว', html_content)
                if waiting_match:
                    result['waiting_count'] = int(waiting_match.group(1))
                    print(f"Found waiting count from Thai text: {result['waiting_count']}")
                    
                # PRIORITY 2: Look for difference in JSON format
                else:    
                    difference_match = re.search(r'difference[^:]*:\s*(\d+)', html_content)
                    if difference_match:
                        result['waiting_count'] = int(difference_match.group(1))
                        print(f"Found waiting count from difference field: {result['waiting_count']}")
                        
                    # PRIORITY 3: Fallback to calculated value based on queue number
                    else:
                        queue_num = int(result['queue_number'])
                        # Standard logic: waiting count is queue_number - 1, with minimum of 0
                        if queue_num <= 1:
                            result['waiting_count'] = 0
                        else:
                            result['waiting_count'] = queue_num - 1
                        print(f"Using calculated waiting count: {result['waiting_count']} (fallback only)")
            except Exception as e:
                print(f"Error extracting waiting count: {e}")
                # Default to 0 if any error occurs
                result['waiting_count'] = 0
                
                # Try a simpler regex as last resort
                try:
                    # Super simplified pattern - just look for a digit after "รอ"
                    simple_match = re.search(r'รอ\s*(\d+)', html_content)
                    if simple_match:
                        result['waiting_count'] = int(simple_match.group(1))
                        print(f"Found waiting count with simplified pattern: {result['waiting_count']}")
                except:
                    pass
            
            return result
        
        def handle_html(html):
            print(f"Received HTML content: {len(html)} characters")
            
            # Save the raw HTML for debugging
            with open("/tmp/raw_print.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            # Extract queue information from the page content
            queue_info = extract_queue_info(html)
            queue_number = queue_info['queue_number']
            date_time = queue_info['timestamp']
            
            # Get waiting count or use a default
            waiting_count = queue_info.get('waiting_count', 15)  # Default to 15 if not found
            
            # Use the extracted queue number directly
            customer_queue = queue_number
            
            # Create a complete receipt as an image
            if DIRECT_THERMAL_PRINTING:
                try:
                    # Create a temporary image file for the complete receipt using Thai receipt generator
                    # Use dynamic waiting count
                    waiting_message = f"รอ {waiting_count} คิว"  # Format as "waiting X queues" in Thai
                    
                    receipt_image_path = self.thai_receipt_generator.create_receipt(
                        service_name="ฝ่ายสินเชื่อ",  # Department name in Thai
                        queue_number=str(customer_queue),  # The queue number in large text
                        timestamp=date_time,
                        waiting_count=waiting_message  # Dynamic waiting count
                    )
                    
                    # Store the image path for printing
                    self.receipt_image_path = receipt_image_path
                    
                    # Set minimal text content (not used when printing image)
                    title = "Your Queue"
                    content = f"Number: {customer_queue}\n"
                except Exception as e:
                    print(f"Error creating Thai text image: {e}")
                    # Fallback to plain text if image creation fails
                    title = "Your Queue"
                    content = f"Number: {queue_number}\n\n"
                    self.receipt_image_path = None
            else:
                # For non-direct printing, just use plain text
                title = "Your Queue"
                content = f"Number: {queue_number}\n\n"
            
            # Current date/time for the receipt
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            footer = f"Printed: {current_time}\nThank you!"
            
            print(f"Printing receipt with title: {title}")
            print(f"Content length: {len(content)} characters")
            
            # Try direct USB printing first
            if DIRECT_THERMAL_PRINTING:
                print("Attempting direct USB printing...")
                try:
                    # Import here to avoid circular imports
                    from thermal_printer import get_printer
                    
                    # Print the actual content with Thai text as image
                    printer = get_printer()
                    if printer.connect():
                        # Use the existing printer connection to print Thai text
                        if hasattr(self, 'receipt_image_path') and self.receipt_image_path:
                            try:
                                # Use a custom receipt method that prints the complete receipt image
                                success = self.print_receipt_image(
                                    printer=printer,
                                    image_path=self.receipt_image_path
                                )
                                
                                # Clean up the temporary image file
                                try:
                                    os.unlink(self.receipt_image_path)
                                except Exception as e:
                                    print(f"Error removing temp file: {e}")
                            except Exception as e:
                                print(f"Error with Thai image printing: {e}")
                                # Fall back to regular text printing
                                success = printer.print_receipt(title, content, footer)
                        else:
                            # Fall back to regular text printing
                            success = printer.print_receipt(title, content, footer)
                        
                        printer.disconnect()
                        if success:
                            print("Receipt printed successfully using direct USB")
                            self.on_print_finished(True)
                            return
                        else:
                            print("Failed to print receipt using direct USB")
                    else:
                        print("Failed to connect to thermal printer")
                except Exception as e:
                    print(f"Error using thermal printer: {e}")
                    import traceback
                    traceback.print_exc()
                    
                # If direct printing fails, fall back to CUPS
                print("Falling back to CUPS printing...")
            
            # Fall back to CUPS printing if direct printing is not available or fails
            try:
                # Save content as text file
                temp_file = "/tmp/pos_print.txt"
                with open(temp_file, "w", encoding="utf-8") as f:
                    # Use the plain text version
                    f.write(f"{title}\n\n{content}\n{footer}")
                
                # Send directly to POS printer using lp command
                printer_name = "xprinter"  # Updated printer name
                print(f"Sending to CUPS printer: {printer_name}")
                result = os.system(f"lp -d {printer_name} {temp_file}")
                print(f"CUPS command result: {result}")
                
                if result == 0:
                    print(f"Silent print job sent to {printer_name} printer via CUPS")
                    self.on_print_finished(True)
                else:
                    print(f"Failed to send print job to {printer_name} printer via CUPS")
                    self.on_print_finished(False)
            except Exception as e:
                print(f"Error with CUPS printing: {e}")
                import traceback
                traceback.print_exc()
                self.on_print_finished(False)

        # Get the plain text content of the page
        print("Requesting page content...")
        self.web_view.page().toPlainText(handle_html)
    
    def on_print_finished(self, success):
        """Callback for print completion"""
        print(f"Print {'succeeded' if success else 'failed'}")

    def handle_console_message(self, message, line, source):
        """Handle console messages from JavaScript (newer PyQt5 versions)"""
        print(f"Console message: {message} (from {source}:{line})")
        if "PRINT_REQUESTED" in message:
            print("Print request detected from console message")
            self.print_page()
        elif "QUEUE_BUTTON_CLICKED" in message:
            print("Queue button click detected")
        elif "QUEUE_API_CALLED" in message or "QUEUE_API_CALLED_AXIOS" in message:
            print("Queue API call detected")

    def handle_console_message_old(self, level, message, line, source):
        """Handle console messages from JavaScript (older PyQt5 versions)"""
        print(f"Console message (old): {message} (from {source}:{line})")
        if "PRINT_REQUESTED" in message:
            print("Print request detected from console message (old)")
            self.print_page()
            
    def print_receipt_image(self, printer, image_path):
        """Print a complete receipt image using the thermal printer"""
        try:
            print("Printing receipt as image...")
            
            # Save the image to a temporary file
            fd, temp_path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            
            # Use the thermal_printer module to print the image
            if hasattr(printer, 'print_image'):
                # If the printer has a print_image method, use it
                success = printer.print_image(image_path)
                return success
            else:
                # Try to use the escpos library directly
                try:
                    from escpos.printer import Usb
                    vendor_id = 0x0483
                    product_id = 0x070b
                    
                    # Disconnect the current connection
                    printer.disconnect()
                    
                    # Create a new connection
                    p = Usb(vendor_id, product_id)
                    p.image(image_path)
                    p.cut()
                    p.close()
                    return True
                except Exception as e:
                    print(f"Error printing image with escpos: {e}")
                    
                    # Fall back to using the print_receipt method
                    print("Falling back to text receipt...")
                    receipt_title = "Your Queue"
                    receipt_content = "Please see display for queue information."
                    receipt_footer = "Thank you!"
                    return printer.print_receipt(receipt_title, receipt_content, receipt_footer)
        except Exception as e:
            print(f"Error printing receipt image: {e}")
            import traceback
            traceback.print_exc()
            return False

    def print_thai_receipt_with_image(self, printer, title, content, footer, image_path, queue_number, timestamp, waiting_count=None):
        """Print a receipt with Thai text as an image using the existing printer connection"""
        try:
            # Check if the thermal_printer module has direct access to the escpos printer
            if hasattr(printer, '_printer'):
                # Some thermal_printer implementations store the escpos printer as _printer
                p = printer._printer
                
                # Print title in English
                p.text(f"\n{title}\n\n")
                
                # Print the Thai text as image
                p.image(image_path)
                
                # Print footer
                p.text(f"\n{footer}\n")
                p.cut()
                return True
            else:
                # Try to access the raw printer commands via your thermal_printer module
                # This depends on how your thermal_printer module is implemented
                # You may need to add a method to your thermal_printer module to print images
                print("Using manual ESC/POS commands to print image")
                
                # Use the existing thermal_printer module to print a complete receipt
                # Combine the Thai title (which we'll handle separately) with the queue info
                receipt_title = "คิวของคุณคือ"  # "Your queue is" in Thai
                
                # Make the queue number large by adding spaces and using multiple lines
                receipt_content = "\n"
                receipt_content += f"    {queue_number}    \n\n"  # Large queue number with spacing
                
                # Add waiting message in Thai
                if waiting_count is None:
                    receipt_content += f"รอ 0 คิว\n"  # Default "Waiting 0 queues" in Thai
                else:
                    receipt_content += f"รอ {waiting_count} คิว\n"  # "Waiting X queues" in Thai
                
                # Add the timestamp
                if timestamp:
                    receipt_content += f"{timestamp}\n"
                else:
                    from datetime import datetime
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    receipt_content += f"{current_time}\n"
                
                # Add a footer with thank you message
                receipt_footer = "Thank you!"
                
                # Print the complete receipt
                success = printer.print_receipt(receipt_title, receipt_content, receipt_footer)
                return success
        except Exception as e:
            print(f"Error in print_thai_receipt_with_image: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_receipt_image(self, service_name, queue_number, date_time, waiting_count=None):
    """Create a complete receipt image with Thai text, service name, queue number and waiting count"""
    try:
        # Find a suitable Thai font
        font_paths = [
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
            "/usr/share/fonts/truetype/thai/TlwgTypo.ttf",
            "/home/mllseminipc/pythonbrowser/THSarabunNew.ttf",  # Check if you have this custom font
            "/usr/share/fonts/truetype/tlwg/TlwgMono.ttf"
        ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                print(f"Using Thai font: {path}")
                break
                
        if not font_path:
            print("No Thai font found, using default")
            # Try to use a default system font as fallback
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            
        # Create an image with the right size for a 58mm receipt (about 384 pixels wide)
        width = 384
        
        # Create fonts in different sizes - match the receipt screenshot
        title_font = ImageFont.truetype(font_path, 25)      # Service name font
        
        # For queue numbers, use a standard sans-serif font that renders digits clearly
        # Try DejaVu Sans first as it has good number rendering
        number_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if not os.path.exists(number_font_path):
            number_font_path = font_path  # Fall back to Thai font if needed
        
        queue_font = ImageFont.truetype(number_font_path, 80)  # Large font for queue number
        date_font = ImageFont.truetype(font_path, 18)       # Smaller font for date
        wait_font = ImageFont.truetype(font_path, 18)       # Font for waiting count
        
        # Create a temporary image to measure text heights
        temp_img = Image.new('RGB', (width, 500), color='white')
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Calculate heights for each element
        title_bbox = temp_draw.textbbox((0, 0), service_name, font=title_font)
        title_height = title_bbox[3] - title_bbox[1]
        
        queue_bbox = temp_draw.textbbox((0, 0), queue_number, font=queue_font)
        queue_height = queue_bbox[3] - queue_bbox[1]
        
        # Use provided date_time or current time
        if not date_time:
            from datetime import datetime
            date_time = datetime.now().strftime("%d/%m/ %H:%M รอ")
            
        date_bbox = temp_draw.textbbox((0, 0), date_time, font=date_font)
        date_height = date_bbox[3] - date_bbox[1]
        
        wait_bbox = temp_draw.textbbox((0, 0), waiting_count, font=wait_font)
        wait_height = wait_bbox[3] - wait_bbox[1]
        
        # Calculate total height with spacing
        total_height = title_height + queue_height + date_height + wait_height + 80  # Add padding
        
        # Create the actual image
        image = Image.new('RGB', (width, total_height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Current Y position for drawing
        y_position = 20
        
        # Draw the service name centered
        title_bbox = draw.textbbox((0, 0), service_name, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, y_position), service_name, font=title_font, fill='black')
        y_position += title_height + 20
        
        # Handle empty or whitespace-only queue numbers
        if not queue_number or queue_number.strip() == "":
            queue_number = "0"  # Default to zero if empty
            
        # Draw the queue number large and centered
        if CUSTOM_DIGIT_RENDERING and queue_number.isdigit():
            # Use our custom digit rendering for numbers
            try:
                # Generate a custom digit image
                digit_size = 70  # Adjust as needed
                num_image = create_number_image(queue_number, digit_size=digit_size)
                
                # Calculate position to center it
                if num_image:
                    num_width, num_height = num_image.size
                    x_pos = (width - num_width) // 2
                    
                    # Paste the number image onto our receipt
                    # Convert binary image (mode '1') to compatible format
                    # Need to convert from '1' mode which is binary (0,1) to 'RGB' which uses (0-255)
                    num_image_rgb = num_image.convert('RGB')
                    image.paste(num_image_rgb, (x_pos, y_position))
                    queue_height = num_height
                else:
                    # Fall back to text rendering if digit image creation failed
                    queue_bbox = draw.textbbox((0, 0), queue_number, font=queue_font)
                    queue_width = queue_bbox[2] - queue_bbox[0]
                    draw.text(((width - queue_width) // 2, y_position), queue_number, font=queue_font, fill='black')
            except Exception as e:
                print(f"Error creating digit image: {e}")
                # Fall back to text rendering
                queue_bbox = draw.textbbox((0, 0), queue_number, font=queue_font)
                queue_width = queue_bbox[2] - queue_bbox[0]
                draw.text(((width - queue_width) // 2, y_position), queue_number, font=queue_font, fill='black')
        else:
            # Fall back to text rendering for non-numeric content
            queue_bbox = draw.textbbox((0, 0), queue_number, font=queue_font)
            queue_width = queue_bbox[2] - queue_bbox[0]
            draw.text(((width - queue_width) // 2, y_position), queue_number, font=queue_font, fill='black')
        
        y_position += queue_height + 15
        
        # Draw the timestamp centered
        date_bbox = draw.textbbox((0, 0), date_time, font=date_font)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(((width - date_width) // 2, y_position), date_time, font=date_font, fill='black')
        y_position += date_height + 15
        
        # Draw waiting count centered
        if waiting_count is None:
            waiting_count = "รอ0คิว"  # Default to 0 if not provided
        elif isinstance(waiting_count, (int, str)) and not waiting_count.startswith("รอ"):
            # If it's just a number, format it as "รอXคิว"
            waiting_count = f"รอ{waiting_count}คิว"
            
        wait_bbox = draw.textbbox((0, 0), waiting_count, font=wait_font)
        wait_width = wait_bbox[2] - wait_bbox[0]
        draw.text(((width - wait_width) // 2, y_position), waiting_count, font=wait_font, fill='black')
        
        # Save to a temporary file
        fd, path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        image.save(path)
        print(f"Thai text image created at {path}")
        return path
            
    except Exception as e:
        print(f"Error creating Thai text image: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    # Get URL from command line if provided
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set up request interceptor for autoplay
    interceptor = WebEngineUrlInterceptor()
    app.web_engine_url_request_interceptor = interceptor
    
    # Platform-specific adjustments
    if IS_LINUX:
        print("Running on Linux")
        # Linux-specific settings can be added here
    elif IS_WINDOWS:
        print("Running on Windows")
        # Windows-specific settings can be added here
    
    # Create and show browser
    browser = KioskBrowser(url)
    browser.show()
    
    print(f"Kiosk browser started - loading {url}")
    print(f"Press Ctrl+Alt+Q to exit" if EXIT_SHORTCUT_ENABLED else "")
    print("Press 'P' to print a receipt")
    
    # Start application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
