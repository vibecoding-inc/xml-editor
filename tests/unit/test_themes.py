#!/usr/bin/env python3
"""
Unit tests for theme functionality.
Tests theme definitions, structure, and integration.
"""

import unittest
import os


class TestThemeColors(unittest.TestCase):
    """Test theme color definitions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Catppuccin Latte colors (Light theme)
        self.latte_colors = {
            "base": "#eff1f5",
            "text": "#4c4f69",
            "mauve": "#8839ef",
            "red": "#d20f39",
            "yellow": "#df8e1d",
            "green": "#40a02b",
            "blue": "#1e66f5",
        }
        
        # Catppuccin Mocha colors (Dark theme)
        self.mocha_colors = {
            "base": "#1e1e2e",
            "text": "#cdd6f4",
            "mauve": "#cba6f7",
            "red": "#f38ba8",
            "yellow": "#f9e2af",
            "green": "#a6e3a1",
            "blue": "#89b4fa",
        }
    
    def test_latte_color_format(self):
        """Test that Latte colors are properly formatted."""
        for key, value in self.latte_colors.items():
            with self.subTest(color=key):
                self.assertTrue(value.startswith('#'), f"{key} should be a hex color")
                self.assertEqual(len(value), 7, f"{key} should be 6-digit hex color")
    
    def test_mocha_color_format(self):
        """Test that Mocha colors are properly formatted."""
        for key, value in self.mocha_colors.items():
            with self.subTest(color=key):
                self.assertTrue(value.startswith('#'), f"{key} should be a hex color")
                self.assertEqual(len(value), 7, f"{key} should be 6-digit hex color")


class TestThemeStructure(unittest.TestCase):
    """Test that theme structure is correct."""
    
    def setUp(self):
        """Set up test fixtures."""
        theme_manager_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'xmleditor', 'theme_manager.py'
        )
        self.theme_manager_path = os.path.abspath(theme_manager_path)
        with open(self.theme_manager_path, 'r') as f:
            self.content = f.read()
    
    def test_theme_definitions_exist(self):
        """Test that all required themes are defined."""
        required_themes = [
            'CATPPUCCIN_LATTE',
            'CATPPUCCIN_FRAPPE',
            'CATPPUCCIN_MACCHIATO',
            'CATPPUCCIN_MOCHA'
        ]
        
        for theme_name in required_themes:
            with self.subTest(theme=theme_name):
                self.assertIn(theme_name, self.content, 
                            f"{theme_name} should be defined")
    
    def test_theme_manager_class_exists(self):
        """Test that ThemeManager class exists."""
        self.assertIn('class ThemeManager', self.content, 
                     "ThemeManager class should exist")
    
    def test_theme_methods_exist(self):
        """Test that key theme methods exist."""
        methods = [
            'detect_system_theme',
            'get_theme',
            'get_system_appropriate_theme'
        ]
        
        for method in methods:
            with self.subTest(method=method):
                self.assertIn(method, self.content, 
                            f"{method} method should exist")


class TestEditorIntegration(unittest.TestCase):
    """Test that XMLEditor has theme support."""
    
    def setUp(self):
        """Set up test fixtures."""
        xml_editor_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'xmleditor', 'xml_editor.py'
        )
        self.xml_editor_path = os.path.abspath(xml_editor_path)
        with open(self.xml_editor_path, 'r') as f:
            self.content = f.read()
    
    def test_theme_manager_imported(self):
        """Test that ThemeManager is imported."""
        self.assertIn('from xmleditor.theme_manager import', self.content,
                     "ThemeManager should be imported")
    
    def test_apply_theme_method_exists(self):
        """Test that apply_theme method exists."""
        self.assertIn('def apply_theme', self.content,
                     "apply_theme method should exist")
    
    def test_lexer_theme_application_exists(self):
        """Test that lexer theme application exists."""
        self.assertIn('_apply_lexer_theme', self.content,
                     "_apply_lexer_theme method should exist")


class TestMainWindowIntegration(unittest.TestCase):
    """Test that MainWindow has theme support."""
    
    def setUp(self):
        """Set up test fixtures."""
        main_window_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'xmleditor', 'main_window.py'
        )
        self.main_window_path = os.path.abspath(main_window_path)
        with open(self.main_window_path, 'r') as f:
            self.content = f.read()
    
    def test_theme_manager_imported(self):
        """Test that ThemeManager is imported."""
        self.assertIn('from xmleditor.theme_manager import', self.content,
                     "ThemeManager should be imported")
    
    def test_theme_menu_exists(self):
        """Test that theme menu is created."""
        self.assertTrue('Theme' in self.content and 'theme_menu' in self.content,
                       "Theme menu should exist")
    
    def test_change_theme_method_exists(self):
        """Test that change_theme method exists."""
        self.assertIn('def change_theme', self.content,
                     "change_theme method should exist")
    
    def test_theme_preference_saved(self):
        """Test that theme preference is saved."""
        self.assertTrue('theme' in self.content and 'settings.setValue' in self.content,
                       "Theme preference should be saved to settings")


if __name__ == '__main__':
    unittest.main()
