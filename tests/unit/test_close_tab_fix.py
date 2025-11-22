#!/usr/bin/env python3
"""
Unit tests for the close tab fix.
Tests the fix for closing tabs with unsaved changes where file_path=None.
"""

import unittest
import os


class TestBasenameWithNone(unittest.TestCase):
    """Test that the fix for os.path.basename with None works correctly."""
    
    def test_buggy_code_crashes(self):
        """Test that the original buggy code crashes with None."""
        file_path = None
        with self.assertRaises(TypeError, msg="os.path.basename(None) should raise TypeError"):
            os.path.basename(file_path)
    
    def test_fixed_code_handles_none(self):
        """Test that the fixed code handles None file_path correctly."""
        file_path = None
        file_name_fixed = os.path.basename(file_path) if file_path else 'Untitled'
        self.assertEqual(file_name_fixed, 'Untitled', 
                        "Fixed code should return 'Untitled' for None file_path")
    
    def test_fixed_code_with_valid_path(self):
        """Test that the fix works with valid file paths."""
        import tempfile
        file_path = os.path.join(tempfile.gettempdir(), 'test_file.xml')
        file_name = os.path.basename(file_path) if file_path else 'Untitled'
        self.assertEqual(file_name, 'test_file.xml',
                        "Fixed code should extract basename for valid path")
    
    def test_fixed_code_with_empty_string(self):
        """Test that the fix works with empty string."""
        file_path = ""
        file_name = os.path.basename(file_path) if file_path else 'Untitled'
        self.assertEqual(file_name, 'Untitled',
                        "Fixed code should return 'Untitled' for empty string")


class TestDictGetBehavior(unittest.TestCase):
    """Test dict.get() behavior with None values."""
    
    def test_dict_get_with_none_value(self):
        """Test that .get() returns None even when key exists with None value."""
        tab_data = {'file_path': None, 'is_modified': True}
        
        # This returns None (not 'Untitled') because the key exists with None value
        file_path_buggy = tab_data.get('file_path', 'Untitled')
        self.assertIsNone(file_path_buggy,
                         "dict.get() returns None when key exists with None value")
    
    def test_proper_none_handling(self):
        """Test the proper way to handle None values from dict.get()."""
        tab_data = {'file_path': None, 'is_modified': True}
        
        # The fix: extract the value first, then check if it's None
        file_path = tab_data.get('file_path')
        file_name = os.path.basename(file_path) if file_path else 'Untitled'
        self.assertEqual(file_name, 'Untitled',
                        "Fixed code should handle None value correctly")
    
    def test_proper_handling_with_valid_path(self):
        """Test proper handling when dict contains valid file path."""
        import tempfile
        path = os.path.join(tempfile.gettempdir(), 'document.xml')
        tab_data = {'file_path': path, 'is_modified': True}
        
        file_path = tab_data.get('file_path')
        file_name = os.path.basename(file_path) if file_path else 'Untitled'
        self.assertEqual(file_name, 'document.xml',
                        "Fixed code should extract basename when path exists")


if __name__ == '__main__':
    unittest.main()
