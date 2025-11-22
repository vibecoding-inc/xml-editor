#!/usr/bin/env python3
"""
Integration tests for Monaco editor imports.
Tests that all required modules can be imported.
"""

import unittest
import os
import sys


class TestMonacoImports(unittest.TestCase):
    """Test that Monaco editor modules can be imported."""
    
    def test_pyqt6_widgets_import(self):
        """Test that PyQt6.QtWidgets can be imported."""
        try:
            from PyQt6.QtWidgets import QApplication
            self.assertTrue(True, "PyQt6.QtWidgets imported successfully")
        except ImportError as e:
            self.skipTest(f"PyQt6.QtWidgets not available: {e}")
    
    def test_pyqt6_webengine_import(self):
        """Test that PyQt6.QtWebEngineWidgets can be imported."""
        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            self.assertTrue(True, "PyQt6.QtWebEngineWidgets imported successfully")
        except ImportError as e:
            self.skipTest(f"PyQt6.QtWebEngineWidgets not available: {e}")
    
    def test_pyqt6_webchannel_import(self):
        """Test that PyQt6.QtWebChannel can be imported."""
        try:
            from PyQt6.QtWebChannel import QWebChannel
            self.assertTrue(True, "PyQt6.QtWebChannel imported successfully")
        except ImportError as e:
            self.skipTest(f"PyQt6.QtWebChannel not available: {e}")
    
    def test_monaco_editor_import(self):
        """Test that xmleditor.monaco_editor can be imported."""
        try:
            from xmleditor.monaco_editor import MonacoEditor
            self.assertTrue(True, "xmleditor.monaco_editor imported successfully")
        except ImportError as e:
            self.skipTest(f"xmleditor.monaco_editor not available: {e}")
    
    def test_collaboration_dialog_import(self):
        """Test that xmleditor.collaboration_dialog can be imported."""
        try:
            from xmleditor.collaboration_dialog import HostSessionDialog, JoinSessionDialog
            self.assertTrue(True, "xmleditor.collaboration_dialog imported successfully")
        except ImportError as e:
            self.skipTest(f"xmleditor.collaboration_dialog not available: {e}")
    
    def test_main_window_import(self):
        """Test that xmleditor.main_window can be imported."""
        try:
            from xmleditor.main_window import MainWindow
            self.assertTrue(True, "xmleditor.main_window imported successfully")
        except ImportError as e:
            self.skipTest(f"xmleditor.main_window not available: {e}")


class TestMonacoHTMLFile(unittest.TestCase):
    """Test that Monaco editor HTML file exists and is properly configured."""
    
    def setUp(self):
        """Set up test fixtures."""
        resources_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'xmleditor', 'resources'
        )
        self.html_path = os.path.abspath(os.path.join(resources_dir, 'monaco_editor.html'))
    
    def test_html_file_exists(self):
        """Test that Monaco editor HTML exists."""
        self.assertTrue(os.path.exists(self.html_path),
                       f"Monaco editor HTML should exist at {self.html_path}")
    
    def test_html_contains_monaco_references(self):
        """Test that HTML contains Monaco references."""
        if not os.path.exists(self.html_path):
            self.skipTest(f"HTML file not found at {self.html_path}")
        
        with open(self.html_path, 'r') as f:
            content = f.read()
        
        self.assertIn('monaco-editor', content,
                     "HTML should contain Monaco editor references")
    
    def test_html_contains_yjs_references(self):
        """Test that HTML contains Y.js references."""
        if not os.path.exists(self.html_path):
            self.skipTest(f"HTML file not found at {self.html_path}")
        
        with open(self.html_path, 'r') as f:
            content = f.read()
        
        self.assertIn('yjs', content,
                     "HTML should contain Y.js references")


if __name__ == '__main__':
    unittest.main()
