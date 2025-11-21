# XML Editor

[![CI](https://github.com/profiluefter/xml-editor/actions/workflows/ci.yml/badge.svg)](https://github.com/profiluefter/xml-editor/actions/workflows/ci.yml)
[![Release](https://github.com/profiluefter/xml-editor/actions/workflows/release.yml/badge.svg)](https://github.com/profiluefter/xml-editor/actions/workflows/release.yml)

A fully-featured cross-platform XML editor desktop application built with Python and PyQt6.

## Features

### Core Features
- **Multiple File Tabs**: Open and edit multiple XML, XSD, and DTD files simultaneously in separate tabs
- **XML Syntax Highlighting**: Advanced syntax highlighting using QScintilla
- **File Operations**: Open, save, and manage XML files with recent files list
- **Auto Save**: Automatically save files every 30 seconds with an easy-to-use checkbox in the File menu
- **Cross-Platform**: Works on Windows, macOS, and Linux

### XML Features
- **Persistent Validation Pane**: Dockable validation panel for continuous validation without modal dialogs
- **XML Validation**: Check well-formedness and validate against schemas
- **XML Schema (XSD) Support**: Full XSD validation with detailed error messages
- **DTD Support**: Validate XML against DTD definitions
- **Schema Generation**: Generate XSD or DTD schemas from XML documents
- **XML Formatting**: Automatic formatting and pretty-printing
- **Tree View**: Visual representation of XML structure that syncs with active tab

### Advanced Features
- **Real-time Collaboration**: Work together on documents with multiple users simultaneously (see [MULTIPLAYER.md](MULTIPLAYER.md))
- **Side-by-Side Editing**: Edit XML and its schema simultaneously in different tabs
- **XPath Queries**: Execute XPath expressions with results display
- **XSLT Transformations**: Apply XSLT stylesheets to transform XML
- **Find & Replace**: Search and replace text in documents
- **Comment/Uncomment**: Toggle XML comments easily
- **Auto-Completion**: Smart code completion
- **Line Numbers**: Easy navigation with line numbers
- **Code Folding**: Collapse/expand XML elements
- **Brace Matching**: Highlight matching tags
- **Undo/Redo**: Full undo/redo support per tab

### Theme Support
- **Modern Color Schemes**: Beautiful Catppuccin themes for enhanced readability
- **System Theme Detection**: Automatically adapts to system dark/light mode
- **Multiple Theme Options**: Choose from Latte (light), Frappé, Macchiato, or Mocha (dark) themes
- **Persistent Theme Settings**: Your theme preference is saved across sessions

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Install from source

1. Clone the repository:
```bash
git clone https://github.com/profiluefter/xml-editor.git
cd xml-editor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the application:
```bash
pip install .
```

### Install from PyPI (when published)
```bash
pip install xml-editor
```

### Install with Nix (Recommended for NixOS users)

**Using Nix Flakes:**
```bash
# Run directly
nix run github:profiluefter/xml-editor

# Install
nix profile install github:profiluefter/xml-editor
```

**Traditional Nix:**
```bash
nix-build
nix-env -f default.nix -i
```

See [NIX.md](NIX.md) for detailed Nix packaging information, including CLI variant and development setup.

## Usage

### Running the application

After installation, run the application using:
```bash
xml-editor
```

Or with Python:
```bash
python -m xmleditor.main
```

### Quick Start

1. **Create a new XML document**: File → New (Ctrl+N)
2. **Open existing XML file**: File → Open (Ctrl+O) - Opens in a new tab
3. **Open multiple files**: Open additional files in separate tabs
4. **Format XML**: XML → Format XML (Ctrl+Shift+F)
5. **Validate XML**: XML → Validate (Ctrl+Shift+V) - Opens validation pane
6. **Generate Schema**: XML → Generate Schema (Ctrl+Shift+G)
7. **Execute XPath**: XML → XPath Query (Ctrl+Shift+X)
8. **Apply XSLT**: XML → XSLT Transform (Ctrl+Shift+T)
9. **Change theme**: View → Theme → Select your preferred theme

### Working with Multiple Files

The editor supports multiple files open simultaneously in tabs:

- **Open Multiple Files**: Each file opens in its own tab with independent editing state
- **Switch Between Tabs**: Click on tabs or use Ctrl+Tab to navigate
- **Close Tabs**: Click the X button on each tab or use Ctrl+W
- **Prevent Duplicates**: Opening the same file again switches to the existing tab
- **Edit XML and Schema Together**: Open XML in one tab and XSD/DTD in another for side-by-side editing

### Using the Validation Pane

The persistent validation pane allows continuous validation without modal dialogs:

- **Toggle Validation Pane**: View → Toggle Validation Panel (Ctrl+Shift+P)
- **Well-Formed Check**: Quick validation that XML is syntactically correct
- **XSD Validation**: Load schema and validate XML against it
- **DTD Validation**: Load DTD and validate XML against it
-- **Load Schema**: Click "Load Schema File" to load .xsd or .dtd files
- **Stay Productive**: Keep validation pane open while editing for instant feedback

### Themes

The editor supports multiple beautiful color schemes powered by [Catppuccin](https://catppuccin.com/):

- **System (Auto)**: Automatically detects your system's dark/light mode and applies the appropriate theme
- **Catppuccin Latte**: A light, warm theme perfect for daytime coding
- **Catppuccin Frappé**: A soft dark theme with muted colors
- **Catppuccin Macchiato**: A medium dark theme with vibrant accents
- **Catppuccin Mocha**: A deep dark theme ideal for low-light environments

To change themes, go to **View → Theme** and select your preferred option. Your selection is saved and will be restored when you reopen the application.

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New File | Ctrl+N |
| Open File | Ctrl+O |
| Save File | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Close Tab | Ctrl+W |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Cut | Ctrl+X |
| Copy | Ctrl+C |
| Paste | Ctrl+V |
| Find | Ctrl+F |
| Replace | Ctrl+H |
| Format XML | Ctrl+Shift+F |
| Validate | Ctrl+Shift+V |
| Generate Schema | Ctrl+Shift+G |
| XPath Query | Ctrl+Shift+X |
| XSLT Transform | Ctrl+Shift+T |
| Toggle Tree View | Ctrl+T |
| Toggle Output Panel | Ctrl+O |
| Toggle Validation Panel | Ctrl+Shift+P |
| Comment/Uncomment | Ctrl+/ |
| Refresh Tree | F5 |
| Host Collaboration | Ctrl+Shift+H |
| Join Collaboration | Ctrl+Shift+J |
| Disconnect Collaboration | Ctrl+Shift+D |

### Multiplayer Collaboration

The XML Editor now supports real-time collaborative editing! Multiple users can work on the same document simultaneously with automatic conflict resolution.

**Quick Start:**
1. Deploy the Cloudflare Worker (see [MULTIPLAYER.md](MULTIPLAYER.md))
2. Use **Collaboration → Host Session** to create a room
3. Share the room name with collaborators
4. They can join using **Collaboration → Join Session**

Features:
- ✓ Real-time synchronization using Y.js CRDTs
- ✓ Automatic conflict resolution
- ✓ No data loss from concurrent edits
- ✓ Easy-to-use host/join dialogs
- ✓ Built on Cloudflare's global edge network

For detailed setup and usage instructions, see [MULTIPLAYER.md](MULTIPLAYER.md).

## Features Comparison with XMLSpy

This XML Editor includes many features similar to XMLSpy:

| Feature | XML Editor | XMLSpy |
|---------|-----------|---------|
| XML Editing with Syntax Highlighting | ✓ | ✓ |
| XML Validation | ✓ | ✓ |
| XSD Schema Support | ✓ | ✓ |
| DTD Support | ✓ | ✓ |
| XPath Queries | ✓ | ✓ |
| XSLT Transformations | ✓ | ✓ |
| XML Tree View | ✓ | ✓ |
| XML Formatting | ✓ | ✓ |
| Find & Replace | ✓ | ✓ |
| Cross-Platform | ✓ | ✗ (Windows only) |
| Open Source | ✓ | ✗ |
| Free | ✓ | ✗ |

## Development

### Project Structure
```
xml-editor/
├── xmleditor/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── main_window.py       # Main window UI
│   ├── xml_editor.py        # XML editor widget
│   ├── xml_utils.py         # XML utilities
│   ├── xml_tree_view.py     # Tree view widget
│   ├── xpath_dialog.py      # XPath query dialog
│   ├── validation_dialog.py # Validation dialog
│   ├── xslt_dialog.py       # XSLT transform dialog
│   └── resources/           # Application resources
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Dependencies

- **PyQt6**: Qt6 bindings for Python
- **PyQt6-QScintilla**: Scintilla editor component for PyQt6
- **lxml**: XML and HTML processing library
- **pygments**: Syntax highlighting library

### Building from Source

```bash
# Install development dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run the application
python -m xmleditor.main
```

### Creating Distribution Package

```bash
# Install build tools
pip install build

# Build the package
python -m build

# This creates:
# - dist/xml-editor-1.0.0.tar.gz (source distribution)
# - dist/xml_editor-1.0.0-py3-none-any.whl (wheel distribution)
```

## Packaging for Different Platforms

### Windows
```bash
# Install PyInstaller
pip install pyinstaller

# Create Windows executable
pyinstaller --name="XML-Editor" --windowed --onefile xmleditor/main.py
```

### macOS
```bash
# Install PyInstaller
pip install pyinstaller

# Create macOS application bundle
pyinstaller --name="XML-Editor" --windowed --onefile xmleditor/main.py
```

### Linux
```bash
# The application can be run directly with Python
# Or create a standalone executable with PyInstaller
pip install pyinstaller
pyinstaller --name="xml-editor" --onefile xmleditor/main.py
```

## CI/CD

The project uses GitHub Actions for continuous integration and deployment. See [CI_CD.md](CI_CD.md) for detailed information about:

- Automated testing on multiple platforms and Python versions
- Nix flake checks including NixOS VM tests
- Automated release builds for all platforms
- Cross-platform package generation

### Quick Reference

```bash
# Run tests locally
python test_functionality.py
python test_schema_generation.py

# Run Nix checks (includes VM test)
nix flake check

# Build with Nix
nix build .#gui
nix build .#cli
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- XML processing with [lxml](https://lxml.de/)
- Code editing with [QScintilla](https://www.riverbankcomputing.com/software/qscintilla/)

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/profiluefter/xml-editor).

## Roadmap

Future enhancements planned:
- JSON to XML conversion
- XML diff and merge tools
- Custom XML snippets
- XML catalog support
- Namespace management
- XML digital signatures
- More XSLT debugging features