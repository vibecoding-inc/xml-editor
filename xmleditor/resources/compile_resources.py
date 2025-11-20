#!/usr/bin/env python3
"""Compile Qt resource files."""
import subprocess
import sys
import os

def compile_qrc():
    """Compile the .qrc file to Python."""
    qrc_file = "resources.qrc"
    output_file = "resources_rc.py"
    
    if not os.path.exists(qrc_file):
        print(f"Error: {qrc_file} not found")
        return False
    
    try:
        # Try pyrcc6 first (PyQt6)
        subprocess.run(["pyrcc6", "-o", output_file, qrc_file], check=True)
        print(f"Successfully compiled {qrc_file} to {output_file}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("pyrcc6 not found, creating manual resource loader...")
        # Create a manual resource loader
        with open(output_file, 'w') as f:
            f.write('''# Generated resource file
import os

def qInitResources():
    """Initialize resources."""
    pass

def qCleanupResources():
    """Cleanup resources."""
    pass

def getResourcePath(name):
    """Get the path to a resource file."""
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, name.lstrip('/'))
''')
        print(f"Created manual resource loader: {output_file}")
        return True

if __name__ == "__main__":
    sys.exit(0 if compile_qrc() else 1)
