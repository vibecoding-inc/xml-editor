#!/usr/bin/env python3
"""
Integration tests for Monaco editor GUI.
Tests that Monaco editor loads correctly and can take screenshots.
"""

import unittest
import os
import sys
import tempfile


class TestMonacoEditorGUI(unittest.TestCase):
    """Test Monaco editor GUI functionality."""
    
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
    
    def test_monaco_editor_creation(self):
        """Test that Monaco editor widget can be created."""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer
            from xmleditor.monaco_editor import MonacoEditor
            from xmleditor.theme_manager import ThemeType
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        
        # Create application
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Create editor
        editor = MonacoEditor(theme_type=ThemeType.CATPPUCCIN_MOCHA)
        editor.setWindowTitle("XML Editor - Monaco Test")
        editor.resize(1200, 800)
        
        # Set some XML content
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="cooking">
        <title lang="en">Everyday Italian</title>
        <author>Giada De Laurentiis</author>
        <year>2005</year>
        <price>30.00</price>
    </book>
</bookstore>'''
        
        editor.set_text(xml_content)
        
        # Verify editor was created
        self.assertIsNotNone(editor, "Editor should be created")
    
    def test_monaco_editor_screenshot(self):
        """Test that Monaco editor can take a screenshot."""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer
            from xmleditor.monaco_editor import MonacoEditor
            from xmleditor.theme_manager import ThemeType
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        
        # Skip if no display available
        if not os.environ.get('DISPLAY') and sys.platform.startswith('linux'):
            self.skipTest("No display available for screenshot test")
        
        # Create application
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Create editor
        editor = MonacoEditor(theme_type=ThemeType.CATPPUCCIN_MOCHA)
        editor.resize(1200, 800)
        
        # Set some XML content
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="children">
        <title lang="en">Harry Potter</title>
        <author>J K. Rowling</author>
        <year>2005</year>
        <price>29.99</price>
    </book>
</bookstore>'''
        
        editor.set_text(xml_content)
        
        # Create temp file for screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            self.temp_screenshot = f.name
        
        # Take screenshot
        pixmap = editor.grab()
        pixmap.save(self.temp_screenshot)
        
        # Verify screenshot file exists and has content
        self.assertTrue(os.path.exists(self.temp_screenshot),
                       "Screenshot file should exist")
        file_size = os.path.getsize(self.temp_screenshot)
        self.assertGreater(file_size, 1000,
                          "Screenshot should be larger than 1KB")


if __name__ == '__main__':
    unittest.main()
