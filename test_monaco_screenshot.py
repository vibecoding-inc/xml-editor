#!/usr/bin/env python3
"""
Create screenshot demonstrating the Monaco editor loading.
"""

import sys
import os
sys.path.insert(0, '/home/runner/work/xml-editor/xml-editor')

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from xmleditor.main_window import MainWindow

def create_monaco_screenshot():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Load a sample XML file
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="cooking">
        <title lang="en">Everyday Italian</title>
        <author>Giada De Laurentiis</author>
        <year>2005</year>
        <price>30.00</price>
    </book>
    <book category="children">
        <title lang="en">Harry Potter</title>
        <author>J K. Rowling</author>
        <year>2005</year>
        <price>29.99</price>
    </book>
</bookstore>"""
    
    # Get current editor and set the XML content
    editor = window.get_current_editor()
    if editor:
        editor.set_text(xml_content)
    
    window.show()
    window.resize(1200, 800)
    
    def capture_screenshot():
        print("Capturing screenshot of Monaco editor...")
        pixmap = window.grab()
        screenshot_path = "/tmp/monaco_editor_screenshot.png"
        pixmap.save(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Also check file size
        if os.path.exists(screenshot_path):
            size = os.path.getsize(screenshot_path)
            print(f"Screenshot size: {size} bytes")
            if size > 10000:
                print("✓ Screenshot appears valid")
            else:
                print("✗ Screenshot may be invalid (too small)")
        
        app.quit()
    
    # Wait for editor to load, then capture
    QTimer.singleShot(2000, capture_screenshot)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(create_monaco_screenshot())
