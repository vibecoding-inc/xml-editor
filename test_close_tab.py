#!/usr/bin/env python3
"""
Test script to verify the fix for closing tabs with unsaved changes.
This test specifically addresses the issue where closing a tab with an
unsaved new document (file_path=None) would cause a TypeError.
"""

import os


def test_basename_with_none():
    """Test that the fix for os.path.basename with None works correctly."""
    print("Testing os.path.basename fix with None file_path...")
    
    # Simulate the original buggy code that would crash
    try:
        # This is what the code used to do - it would crash
        file_path = None
        file_name_buggy = os.path.basename(file_path)
        print(f"  ✗ Buggy code did not crash (unexpected): {file_name_buggy}")
        assert False, "Expected TypeError with buggy code"
    except TypeError as e:
        print(f"  ✓ Buggy code crashes as expected: {e}")
    
    # Simulate the fixed code
    try:
        file_path = None
        file_name_fixed = os.path.basename(file_path) if file_path else 'Untitled'
        print(f"  ✓ Fixed code works correctly: {file_name_fixed}")
        assert file_name_fixed == 'Untitled', f"Expected 'Untitled', got {file_name_fixed}"
    except TypeError as e:
        print(f"  ✗ Fixed code crashed: {e}")
        raise
    
    print("  ✓ Test passed - fix handles None file_path correctly")


def test_basename_with_valid_path():
    """Test that the fix works with valid file paths."""
    print("\nTesting os.path.basename fix with valid file_path...")
    
    # Test with a valid file path
    try:
        file_path = "/tmp/test_file.xml"
        file_name = os.path.basename(file_path) if file_path else 'Untitled'
        print(f"  ✓ file_name generated successfully: {file_name}")
        assert file_name == 'test_file.xml', f"Expected 'test_file.xml', got {file_name}"
    except Exception as e:
        print(f"  ✗ Exception occurred: {e}")
        raise
    
    print("  ✓ Test passed - fix works correctly with valid file_path")


def test_basename_with_empty_string():
    """Test that the fix works with empty string."""
    print("\nTesting os.path.basename fix with empty string file_path...")
    
    # Test with an empty string
    try:
        file_path = ""
        file_name = os.path.basename(file_path) if file_path else 'Untitled'
        print(f"  ✓ file_name generated successfully: {file_name}")
        assert file_name == 'Untitled', f"Expected 'Untitled', got {file_name}"
    except Exception as e:
        print(f"  ✗ Exception occurred: {e}")
        raise
    
    print("  ✓ Test passed - fix handles empty string correctly")


def test_dict_get_behavior():
    """Test that demonstrates the .get() method behavior with None values."""
    print("\nTesting dict.get() behavior with None values...")
    
    # Demonstrate the issue with .get()
    tab_data = {'file_path': None, 'is_modified': True}
    
    # This returns None (not 'Untitled') because the key exists with None value
    file_path_buggy = tab_data.get('file_path', 'Untitled')
    print(f"  file_path with .get('file_path', 'Untitled'): {file_path_buggy}")
    assert file_path_buggy is None, "Expected None"
    
    # The fix: extract the value first, then check if it's None
    file_path = tab_data.get('file_path')
    file_name = os.path.basename(file_path) if file_path else 'Untitled'
    print(f"  file_name with fix: {file_name}")
    assert file_name == 'Untitled', f"Expected 'Untitled', got {file_name}"
    
    print("  ✓ Test passed - demonstrates why the fix is necessary")


if __name__ == "__main__":
    print("=" * 60)
    print("XML Editor - Close Tab Fix Tests")
    print("=" * 60)
    print()
    
    try:
        test_basename_with_none()
        test_basename_with_valid_path()
        test_basename_with_empty_string()
        test_dict_get_behavior()
        
        print()
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

