# Installation Guide

## System Requirements

### Supported Platforms
- Windows 10 or later
- macOS 10.14 or later
- Linux (Ubuntu 20.04+, Fedora 33+, or equivalent)

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- At least 200MB of free disk space

## Installation Methods

### Method 1: Install from PyPI (Recommended)

Once published to PyPI, you can install with:

```bash
pip install xml-editor
```

### Method 2: Install from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/profiluefter/xml-editor.git
   cd xml-editor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the application:**
   ```bash
   pip install .
   ```

### Method 3: Install in Development Mode

For developers who want to modify the code:

```bash
git clone https://github.com/profiluefter/xml-editor.git
cd xml-editor
pip install -e .
```

This creates a symbolic link so your changes are immediately reflected.

## Platform-Specific Instructions

### Windows

1. **Install Python:**
   - Download Python from [python.org](https://www.python.org/downloads/)
   - Check "Add Python to PATH" during installation

2. **Install XML Editor:**
   ```cmd
   pip install xml-editor
   ```

3. **Run the application:**
   ```cmd
   xml-editor
   ```

   Or create a desktop shortcut to:
   ```cmd
   C:\Python3X\Scripts\xml-editor.exe
   ```

### macOS

1. **Install Python (if not already installed):**
   ```bash
   brew install python3
   ```

2. **Install XML Editor:**
   ```bash
   pip3 install xml-editor
   ```

3. **Run the application:**
   ```bash
   xml-editor
   ```

   Or add to PATH:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Linux (Ubuntu/Debian)

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Install XML Editor:**
   ```bash
   pip3 install xml-editor
   ```

3. **Run the application:**
   ```bash
   xml-editor
   ```

   Or create a desktop entry:
   ```bash
   cat > ~/.local/share/applications/xml-editor.desktop << EOF
   [Desktop Entry]
   Name=XML Editor
   Comment=XML Editor with XPath and Schema Support
   Exec=$HOME/.local/bin/xml-editor
   Terminal=false
   Type=Application
   Categories=Development;TextEditor;
   EOF
   ```

### Linux (Fedora/RHEL)

1. **Install dependencies:**
   ```bash
   sudo dnf install python3 python3-pip
   ```

2. **Install XML Editor:**
   ```bash
   pip3 install xml-editor
   ```

3. **Run the application:**
   ```bash
   xml-editor
   ```

## Creating Standalone Executables

For distribution without requiring Python installation:

### Windows Executable

```bash
pip install pyinstaller
pyinstaller --name="XML-Editor" --windowed --onefile xmleditor/main.py
```

The executable will be in `dist/XML-Editor.exe`

### macOS Application

```bash
pip install pyinstaller
pyinstaller --name="XML-Editor" --windowed --onefile xmleditor/main.py
```

The app bundle will be in `dist/XML-Editor.app`

### Linux Binary

```bash
pip install pyinstaller
pyinstaller --name="xml-editor" --onefile xmleditor/main.py
```

The binary will be in `dist/xml-editor`

## Verifying Installation

After installation, verify it works:

```bash
# Check if command is available
xml-editor --version

# Or run directly
python -m xmleditor.main
```

## Troubleshooting

### "Command not found" error

The installation directory is not in your PATH. Try:

```bash
# Find where it's installed
pip show xml-editor

# Add to PATH (Linux/macOS)
export PATH="$HOME/.local/bin:$PATH"

# Or use full path
python -m xmleditor.main
```

### Import errors

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Display/GUI errors on Linux

Install required Qt libraries:

```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# Fedora
sudo dnf install qt6-qtbase-gui
```

### Permission denied

On Linux/macOS, you may need to use `--user` flag:

```bash
pip install --user xml-editor
```

## Uninstallation

To remove XML Editor:

```bash
pip uninstall xml-editor
```

## Updating

To update to the latest version:

```bash
pip install --upgrade xml-editor
```

## Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/profiluefter/xml-editor/issues)
2. Create a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - Error messages
   - Steps to reproduce
