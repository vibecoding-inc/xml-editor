#!/usr/bin/env python3
"""
Unit tests for Monaco editor HTML validation.
Tests that the Monaco editor HTML is correctly structured.
"""

import unittest
import os


class TestMonacoHTMLStructure(unittest.TestCase):
    """Test Monaco editor HTML file structure."""
    
    def setUp(self):
        """Set up test fixtures."""
        html_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'xmleditor', 'resources', 'monaco_editor.html'
        )
        self.html_path = os.path.abspath(html_path)
        
        if os.path.exists(self.html_path):
            with open(self.html_path, 'r') as f:
                self.content = f.read()
        else:
            self.content = None
    
    def test_html_file_exists(self):
        """Test that Monaco editor HTML file exists."""
        self.assertIsNotNone(self.content, f"HTML file should exist at {self.html_path}")
    
    def test_monaco_loader_present(self):
        """Test that Monaco loader.js is present."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        self.assertIn("monaco-editor@0.45.0/min/vs/loader.js", self.content,
                     "Monaco loader.js should be present")
    
    def test_monaco_require_config_present(self):
        """Test that Monaco require config is present."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        self.assertIn("require = {", self.content,
                     "Monaco require config should be present")
    
    def test_monaco_amd_load_present(self):
        """Test that Monaco AMD load is present."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        self.assertIn("require(['vs/editor/editor.main']", self.content,
                     "Monaco AMD load should be present")
    
    def test_yjs_library_present(self):
        """Test that Y.js library is present."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        has_yjs = "yjs@13.6.10" in self.content or "yjs.mjs" in self.content
        self.assertTrue(has_yjs, "Y.js library should be present")
    
    def test_y_websocket_present(self):
        """Test that Y-WebSocket is present."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        has_websocket = "y-websocket@1.5.0" in self.content or "y-websocket.mjs" in self.content
        self.assertTrue(has_websocket, "Y-WebSocket should be present")
    
    def test_qwebchannel_present(self):
        """Test that QWebChannel is present."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        self.assertIn("qrc:///qtwebchannel/qwebchannel.js", self.content,
                     "QWebChannel should be present")
    
    def test_editor_create_present(self):
        """Test that editor creation code is present."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        self.assertIn("monaco.editor.create", self.content,
                     "Editor creation code should be present")
    
    def test_xml_language_present(self):
        """Test that XML language is specified."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        self.assertIn("language: 'xml'", self.content,
                     "XML language should be specified")
    
    def test_content_change_listener_present(self):
        """Test that content change listener is present."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        self.assertIn("onDidChangeModelContent", self.content,
                     "Content change listener should be present")
    
    def test_window_interface_present(self):
        """Test that window interface is exposed."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        self.assertIn("window.monacoEditor", self.content,
                     "Window interface should be exposed")
    
    def test_collaboration_function_present(self):
        """Test that collaboration function is present."""
        self.assertIsNotNone(self.content, "HTML content should be loaded")
        self.assertIn("connectCollaboration", self.content,
                     "Collaboration function should be present")


class TestMonacoHTMLLoadOrder(unittest.TestCase):
    """Test that scripts are loaded in correct order."""
    
    def setUp(self):
        """Set up test fixtures."""
        html_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'xmleditor', 'resources', 'monaco_editor.html'
        )
        self.html_path = os.path.abspath(html_path)
        
        if os.path.exists(self.html_path):
            with open(self.html_path, 'r') as f:
                content = f.read()
                self.lines = content.split('\n')
        else:
            self.lines = None
    
    def test_qwebchannel_before_monaco(self):
        """Test that QWebChannel is loaded before Monaco."""
        if self.lines is None:
            self.skipTest("HTML file not found")
        
        qwebchannel_line = None
        monaco_line = None
        
        for i, line in enumerate(self.lines):
            if 'qwebchannel.js' in line:
                qwebchannel_line = i
            if 'monaco-editor' in line and 'loader.js' in line:
                monaco_line = i
        
        if qwebchannel_line is not None and monaco_line is not None:
            self.assertLess(qwebchannel_line, monaco_line,
                          "QWebChannel should be loaded before Monaco")
    
    def test_loader_before_require(self):
        """Test that Monaco loader.js is loaded before require() call."""
        if self.lines is None:
            self.skipTest("HTML file not found")
        
        monaco_line = None
        require_line = None
        
        for i, line in enumerate(self.lines):
            if 'monaco-editor' in line and 'loader.js' in line:
                monaco_line = i
            if "require(['vs/editor/editor.main']" in line:
                require_line = i
        
        if monaco_line is not None and require_line is not None:
            self.assertLess(monaco_line, require_line,
                          "Monaco loader.js must be loaded before require() call")


if __name__ == '__main__':
    unittest.main()
