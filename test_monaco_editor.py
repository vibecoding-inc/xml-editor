#!/usr/bin/env python3
"""
Test script to verify Monaco editor loads correctly and take a screenshot.
"""

import sys
import os
import time

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from xmleditor.monaco_editor import MonacoEditor
    from xmleditor.theme_manager import ThemeType
    print("✓ Successfully imported required modules")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure PyQt6-WebEngine is installed:")
    print("  pip install PyQt6-WebEngine")
    sys.exit(1)

def take_screenshot():
    """Create a window with Monaco editor and take a screenshot."""
    app = QApplication(sys.argv)
    
    # Create editor
    print("Creating Monaco editor...")
    editor = MonacoEditor(theme_type=ThemeType.CATPPUCCIN_MOCHA)
    editor.setWindowTitle("XML Editor - Monaco Test")
    editor.resize(1200, 800)
    editor.show()
    
    # Set some XML content
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
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
</bookstore>'''
    
    editor.set_text(xml_content)
    print("✓ Editor created and content set")
    
    # Wait for editor to be ready and loaded
    screenshot_taken = [False]
    
    def on_editor_ready():
        print("✓ Monaco editor is ready")
        # Wait a bit more for rendering
        QTimer.singleShot(2000, take_screenshot_now)
    
    def take_screenshot_now():
        try:
            # Take screenshot
            pixmap = editor.grab()
            screenshot_path = os.path.join(os.path.dirname(__file__), 'monaco_editor_test.png')
            pixmap.save(screenshot_path)
            print(f"✓ Screenshot saved to: {screenshot_path}")
            screenshot_taken[0] = True
            
            # Check file size to ensure it's valid
            file_size = os.path.getsize(screenshot_path)
            print(f"✓ Screenshot file size: {file_size} bytes")
            
            if file_size < 1000:
                print("✗ Warning: Screenshot file is suspiciously small")
            
            app.quit()
        except Exception as e:
            print(f"✗ Error taking screenshot: {e}")
            app.quit()
    
    # Connect signal
    editor.editorReady.connect(on_editor_ready)
    
    # Set a timeout in case editor never loads
    QTimer.singleShot(10000, lambda: (
        print("✗ Timeout: Editor did not load within 10 seconds"),
        app.quit()
    ))
    
    print("Waiting for editor to load...")
    result = app.exec()
    
    if screenshot_taken[0]:
        print("\n" + "="*60)
        print("✓ Test completed successfully!")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("✗ Test failed - screenshot not taken")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(take_screenshot())
