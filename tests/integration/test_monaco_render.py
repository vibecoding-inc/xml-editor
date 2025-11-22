#!/usr/bin/env python3
"""
Integration tests for Monaco editor rendering.
Tests that Monaco editor renders correctly with XSD content.
"""

import unittest
import os
import sys
import tempfile


class TestMonacoRender(unittest.TestCase):
    """Test Monaco editor rendering with various content types."""
    
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
    
    def test_monaco_render_with_xsd(self):
        """Test rendering Monaco editor with XSD content."""
        try:
            from PyQt6.QtWidgets import QApplication
            from xmleditor.main_window import MainWindow
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        
        # Skip if no display available
        if not os.environ.get('DISPLAY') and sys.platform.startswith('linux'):
            self.skipTest("No display available for render test")
        
        # Create application
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Create main window
        window = MainWindow()
        
        # Load sample XSD file if it exists
        xsd_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'samples', 'books.xsd'
        )
        xsd_path = os.path.abspath(xsd_path)
        
        if os.path.exists(xsd_path):
            with open(xsd_path, 'r') as f:
                content = f.read()
            
            # Get current editor and set content
            editor = window.get_current_editor()
            if editor:
                editor.set_text(content)
        
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
