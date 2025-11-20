#!/usr/bin/env python3
"""
Build script for creating distribution packages.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print status."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main build script."""
    print("XML Editor - Build and Package Script")
    print("="*60)
    
    # Ensure we're in the right directory
    if not os.path.exists('setup.py'):
        print("Error: setup.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Clean previous builds
    if run_command("rm -rf build dist *.egg-info", "Cleaning previous builds"):
        pass
    
    # Install build dependencies
    if not run_command("pip install build wheel twine", "Installing build dependencies"):
        print("\nFailed to install build dependencies")
        sys.exit(1)
    
    # Build source distribution
    if not run_command("python -m build --sdist", "Building source distribution"):
        print("\nFailed to build source distribution")
        sys.exit(1)
    
    # Build wheel distribution
    if not run_command("python -m build --wheel", "Building wheel distribution"):
        print("\nFailed to build wheel distribution")
        sys.exit(1)
    
    # List created files
    print("\n" + "="*60)
    print("Build artifacts created:")
    print("="*60)
    
    if os.path.exists('dist'):
        for file in os.listdir('dist'):
            file_path = os.path.join('dist', file)
            file_size = os.path.getsize(file_path)
            print(f"  - {file} ({file_size:,} bytes)")
    
    print("\n" + "="*60)
    print("Build completed successfully!")
    print("="*60)
    print("\nTo install the package locally:")
    print("  pip install dist/xml_editor-1.0.0-py3-none-any.whl")
    print("\nTo upload to PyPI (requires credentials):")
    print("  twine upload dist/*")
    print("\nTo create platform-specific executables:")
    print("  pip install pyinstaller")
    print("  pyinstaller --name='XML-Editor' --windowed --onefile xmleditor/main.py")
    print("="*60)

if __name__ == "__main__":
    main()
