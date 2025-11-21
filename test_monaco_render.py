#!/usr/bin/env python3
"""
Create screenshot demonstrating the Monaco editor with real rendering.
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
    
    # Load the sample XSD file
    xsd_path = "/home/runner/work/xml-editor/xml-editor/samples/books.xsd"
    with open(xsd_path, 'r') as f:
        content = f.read()
    
    # Get current editor and set the XSD content
    editor = window.get_current_editor()
    if editor:
        editor.set_text(content)
    
    window.show()
    window.resize(1200, 800)
    
    def capture_screenshot():
        print("Capturing screenshot of Monaco editor...")
        pixmap = window.grab()
        screenshot_path = "/tmp/monaco_editor_working.png"
        pixmap.save(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Check file size
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
