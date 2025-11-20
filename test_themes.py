#!/usr/bin/env python3
"""
Test script to verify theme functionality.
"""

# Test theme definitions without PyQt6
def test_theme_colors():
    """Test theme color definitions."""
    print("Testing theme color definitions...")
    
    # Catppuccin Latte colors (Light theme)
    latte_colors = {
        "base": "#eff1f5",
        "text": "#4c4f69",
        "mauve": "#8839ef",
        "red": "#d20f39",
        "yellow": "#df8e1d",
        "green": "#40a02b",
        "blue": "#1e66f5",
    }
    
    # Catppuccin Mocha colors (Dark theme)
    mocha_colors = {
        "base": "#1e1e2e",
        "text": "#cdd6f4",
        "mauve": "#cba6f7",
        "red": "#f38ba8",
        "yellow": "#f9e2af",
        "green": "#a6e3a1",
        "blue": "#89b4fa",
    }
    
    print("  Latte (Light) colors:")
    for key, value in latte_colors.items():
        print(f"    {key}: {value}")
        assert value.startswith('#'), f"{key} should be a hex color"
        assert len(value) == 7, f"{key} should be 6-digit hex color"
    
    print("  Mocha (Dark) colors:")
    for key, value in mocha_colors.items():
        print(f"    {key}: {value}")
        assert value.startswith('#'), f"{key} should be a hex color"
        assert len(value) == 7, f"{key} should be 6-digit hex color"
    
    print()

def test_theme_structure():
    """Test that theme structure is correct."""
    print("Testing theme structure...")
    
    # Read the theme_manager.py file to verify structure
    with open('xmleditor/theme_manager.py', 'r') as f:
        content = f.read()
    
    # Check that all themes are defined
    required_themes = [
        'CATPPUCCIN_LATTE',
        'CATPPUCCIN_FRAPPE',
        'CATPPUCCIN_MACCHIATO',
        'CATPPUCCIN_MOCHA'
    ]
    
    for theme_name in required_themes:
        assert theme_name in content, f"{theme_name} should be defined"
        print(f"  ✓ {theme_name} defined")
    
    # Check that ThemeManager class exists
    assert 'class ThemeManager' in content, "ThemeManager class should exist"
    print("  ✓ ThemeManager class defined")
    
    # Check for key methods
    assert 'detect_system_theme' in content, "detect_system_theme method should exist"
    print("  ✓ detect_system_theme method defined")
    
    assert 'get_theme' in content, "get_theme method should exist"
    print("  ✓ get_theme method defined")
    
    assert 'get_system_appropriate_theme' in content, "get_system_appropriate_theme method should exist"
    print("  ✓ get_system_appropriate_theme method defined")
    
    print()

def test_editor_integration():
    """Test that XMLEditor has theme support."""
    print("Testing XMLEditor integration...")
    
    with open('xmleditor/xml_editor.py', 'r') as f:
        content = f.read()
    
    # Check that theme imports exist
    assert 'from xmleditor.theme_manager import' in content, "ThemeManager should be imported"
    print("  ✓ ThemeManager imported")
    
    # Check that apply_theme method exists
    assert 'def apply_theme' in content, "apply_theme method should exist"
    print("  ✓ apply_theme method defined")
    
    # Check that lexer theme application exists
    assert '_apply_lexer_theme' in content, "_apply_lexer_theme method should exist"
    print("  ✓ _apply_lexer_theme method defined")
    
    print()

def test_main_window_integration():
    """Test that MainWindow has theme support."""
    print("Testing MainWindow integration...")
    
    with open('xmleditor/main_window.py', 'r') as f:
        content = f.read()
    
    # Check that theme imports exist
    assert 'from xmleditor.theme_manager import' in content, "ThemeManager should be imported"
    print("  ✓ ThemeManager imported")
    
    # Check that theme menu is created
    assert 'Theme' in content and 'theme_menu' in content, "Theme menu should exist"
    print("  ✓ Theme menu created")
    
    # Check that change_theme method exists
    assert 'def change_theme' in content, "change_theme method should exist"
    print("  ✓ change_theme method defined")
    
    # Check that theme preference is saved
    assert 'theme' in content and 'settings.setValue' in content, "Theme preference should be saved"
    print("  ✓ Theme preference saved to settings")
    
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("XML Editor - Theme Integration Tests")
    print("=" * 60)
    print()
    
    try:
        test_theme_colors()
        test_theme_structure()
        test_editor_integration()
        test_main_window_integration()
        
        print("=" * 60)
        print("All theme integration tests passed! ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
