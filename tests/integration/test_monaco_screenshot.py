#!/usr/bin/env python3
"""
Integration tests for Monaco editor screenshot functionality.
Tests that Monaco editor can capture screenshots correctly.
"""

import unittest
import os
import sys
import tempfile


class TestMonacoScreenshot(unittest.TestCase):
    """Test Monaco editor screenshot capture."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = None
        self.temp_screenshot = None
    
    def tearDown(self):
        """Clean up after tests."""
        if self.app is not None:
            self.app.quit()
        if self.temp_screenshot and os.path.exists(self.temp_screenshot):
            try:
                os.remove(self.temp_screenshot)
            except:
                pass
    
    def test_monaco_screenshot_with_xml(self):
        """Test taking screenshot of Monaco editor with XML content."""
        try:
            from PyQt6.QtWidgets import QApplication
            from xmleditor.main_window import MainWindow
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        
        # Skip if no display available
        if not os.environ.get('DISPLAY') and sys.platform.startswith('linux'):
            self.skipTest("No display available for screenshot test")
        
        # Create application
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Create main window
        window = MainWindow()
        
        # Set XML content
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
        
        # Get current editor and set content
        editor = window.get_current_editor()
        if editor:
            editor.set_text(xml_content)
        
        window.resize(1200, 800)
        
        # Create temp file for screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            self.temp_screenshot = f.name
        
        # Take screenshot
        pixmap = window.grab()
        pixmap.save(self.temp_screenshot)
        
        # Verify screenshot file exists and has content
        self.assertTrue(os.path.exists(self.temp_screenshot),
                       "Screenshot file should exist")
        file_size = os.path.getsize(self.temp_screenshot)
        self.assertGreater(file_size, 10000,
                          "Screenshot should be larger than 10KB")


if __name__ == '__main__':
    unittest.main()
