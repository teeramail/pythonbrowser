@echo off
echo Installing required packages...
pip install PyQt5==5.15.9 PyQtWebEngine==5.15.6

echo Running kiosk browser...
python kiosk_browser.py
