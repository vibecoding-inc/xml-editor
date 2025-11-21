#!/usr/bin/env python3
"""
Simple test to verify Monaco editor module can be imported.
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing XML Editor Monaco imports...")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✓ PyQt6.QtWidgets imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyQt6.QtWidgets: {e}")
        return False
    
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("✓ PyQt6.QtWebEngineWidgets imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyQt6.QtWebEngineWidgets: {e}")
        return False
    
    try:
        from PyQt6.QtWebChannel import QWebChannel
        print("✓ PyQt6.QtWebChannel imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyQt6.QtWebChannel: {e}")
        return False
    
    try:
        from xmleditor.monaco_editor import MonacoEditor
        print("✓ xmleditor.monaco_editor imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import xmleditor.monaco_editor: {e}")
        return False
    
    try:
        from xmleditor.collaboration_dialog import HostSessionDialog, JoinSessionDialog
        print("✓ xmleditor.collaboration_dialog imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import xmleditor.collaboration_dialog: {e}")
        return False
    
    try:
        from xmleditor.main_window import MainWindow
        print("✓ xmleditor.main_window imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import xmleditor.main_window: {e}")
        return False
    
    # Check that HTML file exists
    resources_dir = os.path.join(os.path.dirname(__file__), 'xmleditor', 'resources')
    html_path = os.path.join(resources_dir, 'monaco_editor.html')
    if os.path.exists(html_path):
        print(f"✓ Monaco editor HTML found at: {html_path}")
        
        # Check HTML content
        with open(html_path, 'r') as f:
            content = f.read()
            if 'monaco-editor' in content:
                print("✓ Monaco editor HTML contains Monaco references")
            else:
                print("✗ Monaco editor HTML does not contain Monaco references")
                return False
            
            if 'yjs' in content:
                print("✓ Monaco editor HTML contains Y.js references")
            else:
                print("✗ Monaco editor HTML does not contain Y.js references")
                return False
    else:
        print(f"✗ Monaco editor HTML not found at: {html_path}")
        return False
    
    print("=" * 60)
    print("✓ All import tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
