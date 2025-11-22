#!/usr/bin/env python3
"""
Unit tests for multiplayer collaboration implementation.
Validates that all required files exist and are properly structured.
"""

import unittest
import os
import json


class TestPythonFiles(unittest.TestCase):
    """Test that Python files exist and have valid syntax."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.base_dir = os.path.abspath(self.base_dir)
    
    def _check_python_syntax(self, path):
        """Check Python file syntax."""
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')
    
    def test_monaco_editor_exists(self):
        """Test that Monaco editor widget exists."""
        path = os.path.join(self.base_dir, 'xmleditor', 'monaco_editor.py')
        self.assertTrue(os.path.exists(path), f"Monaco editor should exist at {path}")
    
    def test_monaco_editor_syntax(self):
        """Test that Monaco editor has valid Python syntax."""
        path = os.path.join(self.base_dir, 'xmleditor', 'monaco_editor.py')
        if os.path.exists(path):
            self._check_python_syntax(path)
    
    def test_collaboration_dialog_exists(self):
        """Test that collaboration dialogs exist."""
        path = os.path.join(self.base_dir, 'xmleditor', 'collaboration_dialog.py')
        self.assertTrue(os.path.exists(path), f"Collaboration dialog should exist at {path}")
    
    def test_collaboration_dialog_syntax(self):
        """Test that collaboration dialog has valid Python syntax."""
        path = os.path.join(self.base_dir, 'xmleditor', 'collaboration_dialog.py')
        if os.path.exists(path):
            self._check_python_syntax(path)
    
    def test_main_window_exists(self):
        """Test that main window exists."""
        path = os.path.join(self.base_dir, 'xmleditor', 'main_window.py')
        self.assertTrue(os.path.exists(path), f"Main window should exist at {path}")
    
    def test_main_window_syntax(self):
        """Test that main window has valid Python syntax."""
        path = os.path.join(self.base_dir, 'xmleditor', 'main_window.py')
        if os.path.exists(path):
            self._check_python_syntax(path)


class TestWebFiles(unittest.TestCase):
    """Test that web files exist and are not empty."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.base_dir = os.path.abspath(self.base_dir)
    
    def test_monaco_html_exists(self):
        """Test that Monaco editor HTML exists."""
        path = os.path.join(self.base_dir, 'xmleditor', 'resources', 'monaco_editor.html')
        self.assertTrue(os.path.exists(path), f"Monaco HTML should exist at {path}")
    
    def test_monaco_html_not_empty(self):
        """Test that Monaco editor HTML is not empty."""
        path = os.path.join(self.base_dir, 'xmleditor', 'resources', 'monaco_editor.html')
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
            self.assertTrue(content.strip(), "Monaco HTML should not be empty")
    
    def test_cloudflare_worker_exists(self):
        """Test that Cloudflare Worker exists."""
        path = os.path.join(self.base_dir, 'cloudflare-worker', 'src', 'index.js')
        self.assertTrue(os.path.exists(path), f"Cloudflare Worker should exist at {path}")
    
    def test_cloudflare_worker_not_empty(self):
        """Test that Cloudflare Worker is not empty."""
        path = os.path.join(self.base_dir, 'cloudflare-worker', 'src', 'index.js')
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
            self.assertTrue(content.strip(), "Cloudflare Worker should not be empty")


class TestConfigurationFiles(unittest.TestCase):
    """Test that configuration files exist and are valid."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.base_dir = os.path.abspath(self.base_dir)
    
    def test_wrangler_config_exists(self):
        """Test that Wrangler config exists."""
        path = os.path.join(self.base_dir, 'cloudflare-worker', 'wrangler.toml')
        self.assertTrue(os.path.exists(path), f"Wrangler config should exist at {path}")
    
    def test_worker_package_json_exists(self):
        """Test that Worker package.json exists."""
        path = os.path.join(self.base_dir, 'cloudflare-worker', 'package.json')
        self.assertTrue(os.path.exists(path), f"Worker package.json should exist at {path}")
    
    def test_worker_package_json_valid(self):
        """Test that Worker package.json is valid JSON."""
        path = os.path.join(self.base_dir, 'cloudflare-worker', 'package.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                json.load(f)  # Will raise exception if invalid


class TestDocumentation(unittest.TestCase):
    """Test that documentation files exist."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.base_dir = os.path.abspath(self.base_dir)
    
    def test_multiplayer_doc_exists(self):
        """Test that multiplayer documentation exists."""
        path = os.path.join(self.base_dir, 'MULTIPLAYER.md')
        self.assertTrue(os.path.exists(path), f"MULTIPLAYER.md should exist at {path}")
    
    def test_worker_readme_exists(self):
        """Test that Worker README exists."""
        path = os.path.join(self.base_dir, 'cloudflare-worker', 'README.md')
        self.assertTrue(os.path.exists(path), f"Worker README should exist at {path}")


class TestDependencies(unittest.TestCase):
    """Test that required dependencies are listed."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.base_dir = os.path.abspath(self.base_dir)
    
    def test_pyqt6_webengine_in_requirements(self):
        """Test that PyQt6-WebEngine is in requirements.txt."""
        req_path = os.path.join(self.base_dir, 'requirements.txt')
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                requirements = f.read()
            self.assertIn('PyQt6-WebEngine', requirements,
                         "PyQt6-WebEngine should be in requirements.txt")


if __name__ == '__main__':
    unittest.main()
