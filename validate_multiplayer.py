#!/usr/bin/env python3
"""
Simple validation script for multiplayer collaboration implementation.
This script checks for common issues without requiring PyQt6 to be installed.
"""

import os
import sys
import json

def check_file_exists(path, description):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} not found: {path}")
        return False

def check_python_syntax(path):
    """Check Python file syntax."""
    try:
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')
        print(f"✓ Python syntax valid: {path}")
        return True
    except SyntaxError as e:
        print(f"✗ Python syntax error in {path}: {e}")
        return False

def check_javascript_basic(path):
    """Basic JavaScript syntax check."""
    try:
        with open(path, 'r') as f:
            content = f.read()
        # Very basic checks
        if content.strip():
            print(f"✓ JavaScript file not empty: {path}")
            return True
        else:
            print(f"✗ JavaScript file is empty: {path}")
            return False
    except Exception as e:
        print(f"✗ Error reading JavaScript file {path}: {e}")
        return False

def check_json_valid(path):
    """Check if JSON file is valid."""
    try:
        with open(path, 'r') as f:
            json.load(f)
        print(f"✓ JSON valid: {path}")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ JSON error in {path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error reading {path}: {e}")
        return False

def main():
    """Run validation checks."""
    print("=" * 60)
    print("Multiplayer Collaboration Implementation Validation")
    print("=" * 60)
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    checks_passed = 0
    checks_total = 0
    
    # Check Python files
    python_files = [
        ("xmleditor/monaco_editor.py", "Monaco editor widget"),
        ("xmleditor/collaboration_dialog.py", "Collaboration dialogs"),
        ("xmleditor/main_window.py", "Main window"),
    ]
    
    print("Checking Python files:")
    print("-" * 60)
    for file_path, description in python_files:
        full_path = os.path.join(base_dir, file_path)
        checks_total += 1
        if check_file_exists(full_path, description):
            checks_total += 1
            if check_python_syntax(full_path):
                checks_passed += 2
            else:
                checks_passed += 1
        print()
    
    # Check HTML/JS files
    web_files = [
        ("xmleditor/resources/monaco_editor.html", "Monaco editor HTML"),
        ("cloudflare-worker/src/index.js", "Cloudflare Worker"),
    ]
    
    print("Checking web files:")
    print("-" * 60)
    for file_path, description in web_files:
        full_path = os.path.join(base_dir, file_path)
        checks_total += 1
        if check_file_exists(full_path, description):
            checks_total += 1
            if check_javascript_basic(full_path):
                checks_passed += 2
            else:
                checks_passed += 1
        print()
    
    # Check configuration files
    config_files = [
        ("cloudflare-worker/wrangler.toml", "Wrangler config"),
        ("cloudflare-worker/package.json", "Worker package.json"),
    ]
    
    print("Checking configuration files:")
    print("-" * 60)
    for file_path, description in config_files:
        full_path = os.path.join(base_dir, file_path)
        checks_total += 1
        if check_file_exists(full_path, description):
            if file_path.endswith('.json'):
                checks_total += 1
                if check_json_valid(full_path):
                    checks_passed += 2
                else:
                    checks_passed += 1
            else:
                checks_passed += 1
        print()
    
    # Check documentation
    doc_files = [
        ("MULTIPLAYER.md", "Multiplayer documentation"),
        ("cloudflare-worker/README.md", "Worker README"),
    ]
    
    print("Checking documentation:")
    print("-" * 60)
    for file_path, description in doc_files:
        full_path = os.path.join(base_dir, file_path)
        checks_total += 1
        if check_file_exists(full_path, description):
            checks_passed += 1
        print()
    
    # Check dependencies
    print("Checking dependencies:")
    print("-" * 60)
    req_path = os.path.join(base_dir, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            requirements = f.read()
        checks_total += 1
        if 'PyQt6-WebEngine' in requirements:
            print("✓ PyQt6-WebEngine in requirements.txt")
            checks_passed += 1
        else:
            print("✗ PyQt6-WebEngine not in requirements.txt")
    print()
    
    # Summary
    print("=" * 60)
    print(f"Validation Summary: {checks_passed}/{checks_total} checks passed")
    print("=" * 60)
    
    if checks_passed == checks_total:
        print("\n✓ All validation checks passed!")
        return 0
    else:
        print(f"\n✗ {checks_total - checks_passed} check(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
