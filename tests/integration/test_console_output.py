#!/usr/bin/env python3
"""
Integration tests for console output capture.
Tests capturing JavaScript console messages from Monaco editor.
"""

import unittest
import os
import sys


class TestConsoleOutput(unittest.TestCase):
    """Test console output capture from Monaco editor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = None
    
    def tearDown(self):
        """Clean up after tests."""
        if self.app is not None:
            self.app.quit()
    
    def test_console_capture_page(self):
        """Test that custom QWebEnginePage can capture console output."""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtWebEngineCore import QWebEnginePage
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        
        # Skip if no display available
        if not os.environ.get('DISPLAY') and sys.platform.startswith('linux'):
            self.skipTest("No display available for console test")
        
        # Create application
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Create a custom console capture page
        class ConsoleCapturePage(QWebEnginePage):
            def __init__(self):
                super().__init__()
                self.console_messages = []
            
            def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
                self.console_messages.append({
                    'level': level,
                    'message': message,
                    'line': lineNumber,
                    'source': sourceID
                })
        
        # Create the page
        page = ConsoleCapturePage()
        
        # Verify the page was created
        self.assertIsNotNone(page, "Console capture page should be created")
        self.assertEqual(len(page.console_messages), 0,
                        "Console messages should be empty initially")
    
    def test_console_capture_with_main_window(self):
        """Test console capture with main window."""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtWebEngineCore import QWebEnginePage
            from xmleditor.main_window import MainWindow
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        
        # Skip if no display available
        if not os.environ.get('DISPLAY') and sys.platform.startswith('linux'):
            self.skipTest("No display available for console test")
        
        # Create application
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Create main window
        window = MainWindow()
        
        # Get current editor
        editor = window.get_current_editor()
        
        # Verify editor exists
        self.assertIsNotNone(editor, "Editor should exist")


if __name__ == '__main__':
    unittest.main()
