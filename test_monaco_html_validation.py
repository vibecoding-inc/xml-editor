#!/usr/bin/env python3
"""
Validate that the Monaco editor HTML is correctly structured.
"""

import os
import sys

def validate_html():
    """Check the Monaco editor HTML file for correct structure."""
    print("Validating Monaco Editor HTML...")
    print("=" * 60)
    
    html_path = "/home/runner/work/xml-editor/xml-editor/xmleditor/resources/monaco_editor.html"
    
    if not os.path.exists(html_path):
        print(f"✗ HTML file not found: {html_path}")
        return False
    
    with open(html_path, 'r') as f:
        content = f.read()
    
    checks = [
        ("Monaco loader.js", "monaco-editor@0.45.0/min/vs/loader.js"),
        ("Monaco require config", "require = {"),
        ("Monaco AMD load", "require(['vs/editor/editor.main']"),
        ("Y.js library", "yjs@13.6.10"),
        ("Y-Monaco binding", "y-monaco@0.1.6"),
        ("Y-WebSocket", "y-websocket@1.5.0"),
        ("QWebChannel", "qrc:///qtwebchannel/qwebchannel.js"),
        ("Editor create", "monaco.editor.create"),
        ("XML language", "language: 'xml'"),
        ("Content change listener", "onDidChangeModelContent"),
        ("Window interface", "window.monacoEditor"),
        ("Collaboration function", "connectCollaboration"),
    ]
    
    all_passed = True
    for check_name, check_string in checks:
        if check_string in content:
            print(f"✓ {check_name}: found")
        else:
            print(f"✗ {check_name}: NOT FOUND")
            all_passed = False
    
    print("=" * 60)
    
    # Additional structural checks
    print("\nStructural checks:")
    
    # Check script loading order
    lines = content.split('\n')
    qwebchannel_line = None
    yjs_line = None
    monaco_line = None
    require_line = None
    
    for i, line in enumerate(lines):
        if 'qwebchannel.js' in line:
            qwebchannel_line = i
        if 'yjs@' in line and qwebchannel_line:
            yjs_line = i
        if 'monaco-editor' in line and 'loader.js' in line:
            monaco_line = i
        if "require(['vs/editor/editor.main']" in line:
            require_line = i
    
    if qwebchannel_line and monaco_line:
        if qwebchannel_line < monaco_line:
            print("✓ QWebChannel loaded before Monaco")
        else:
            print("✗ Warning: QWebChannel should be loaded before Monaco")
    
    if monaco_line and require_line:
        if monaco_line < require_line:
            print("✓ Monaco loader.js loaded before require() call")
        else:
            print("✗ Error: Monaco loader.js must be loaded before require() call")
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✓ All validation checks passed!")
        print("\nThe Monaco editor HTML is correctly structured.")
        print("Note: Actual rendering requires a display with GPU support.")
        return True
    else:
        print("✗ Some validation checks failed")
        return False

if __name__ == "__main__":
    success = validate_html()
    sys.exit(0 if success else 1)
