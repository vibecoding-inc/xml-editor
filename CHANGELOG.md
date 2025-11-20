# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-20

### Added

#### Core Features
- XML editor with QScintilla-based syntax highlighting
- Cross-platform support (Windows, macOS, Linux)
- Modern PyQt6-based graphical user interface

#### File Operations
- New document creation with XML template
- Open XML files with file browser
- Save and Save As functionality
- Recent files list (last 10 files)
- Window state and settings persistence

#### XML Editing Features
- Syntax highlighting for XML elements, attributes, values, comments
- Line numbers with adjustable width
- Code folding for XML elements
- Brace matching for opening/closing tags
- Auto-indentation with smart indent
- Indentation guides
- Current line highlighting
- Edge marker at column 80
- Full UTF-8 support
- Unlimited undo/redo
- Auto-completion with threshold

#### XML Validation
- Well-formedness checking
- XSD (XML Schema) validation
  - Load schema from file or paste
  - Detailed error reporting with line numbers
  - Support for complex types, attributes, sequences
- DTD validation
  - Load DTD from file or paste
  - Comprehensive error messages

#### XPath Support
- XPath query dialog
- XPath 1.0 full specification support
- Example queries in tooltip
- Formatted results display
- Support for:
  - Element selection
  - Attribute selection
  - Predicates and filters
  - Functions (count, sum, etc.)
  - Position-based selection

#### XSLT Transformation
- XSLT 1.0 transformation support
- Load stylesheet from file or paste
- Result preview
- Save transformation result
- Apply result to editor
- Template matching and application
- Variables and parameters support

#### XML Tree View
- Hierarchical structure visualization
- Element names display
- Text content preview (truncated)
- Attributes with values
- Expand/collapse functionality
- Alternating row colors
- Tooltips with full content
- Manual refresh (F5)

#### XML Formatting
- Pretty-print XML documents
- Configurable indentation (default: 2 spaces)
- Proper line breaks
- XML declaration preservation
- Encoding preservation

#### Edit Operations
- Undo/Redo (Ctrl+Z/Ctrl+Y)
- Cut/Copy/Paste (Ctrl+X/C/V)
- Find text (Ctrl+F)
- Replace text (Ctrl+H)
- Comment/Uncomment XML (Ctrl+/)
- Line and block commenting

#### User Interface
- Menu bar with organized commands
- Toolbar with quick access buttons
- Status bar with file information
- Resizable editor and tree view panels
- Dockable output panel for errors
- Toggle tree view (Ctrl+T)
- Toggle output panel (Ctrl+O)
- Word wrap option
- Fusion theme styling

#### Keyboard Shortcuts
- File: Ctrl+N (New), Ctrl+O (Open), Ctrl+S (Save), Ctrl+Shift+S (Save As)
- Edit: Ctrl+Z (Undo), Ctrl+Y (Redo), Ctrl+F (Find), Ctrl+H (Replace)
- XML: Ctrl+Shift+F (Format), Ctrl+Shift+V (Validate), Ctrl+Shift+X (XPath), Ctrl+Shift+T (XSLT)
- View: Ctrl+T (Tree), Ctrl+O (Output), F5 (Refresh)
- Comment: Ctrl+/ (Toggle Comment)

#### Documentation
- Comprehensive README with feature overview
- Detailed installation guide (INSTALL.md)
- Complete user guide (USER_GUIDE.md)
- Full feature documentation (FEATURES.md)
- Sample XML files with examples
- Sample XSD schemas
- Sample XSLT stylesheets

#### Development
- setup.py for package installation
- pyproject.toml for modern Python packaging
- requirements.txt for dependencies
- Build script for distribution packages
- Entry points for console and GUI applications
- Test suite for core functionality
- .gitignore for Python projects
- MIT License

#### Packaging
- Wheel distribution (.whl)
- Source distribution (.tar.gz)
- Console entry point (xml-editor)
- GUI entry point (xml-editor-gui)
- Cross-platform compatibility
- PyPI-ready package structure

### Sample Files
- books.xml - Bookstore catalog example
- books.xsd - Schema for books.xml
- books_to_html.xsl - XSLT transformation example
- employees.xml - Employee data example
- products.xml - Product catalog example
- Sample README with usage examples

### Dependencies
- PyQt6 >= 6.6.0 (Qt6 bindings)
- PyQt6-QScintilla >= 2.14.0 (Code editor component)
- lxml >= 5.0.0 (XML processing)
- pygments >= 2.17.0 (Syntax highlighting)

### Technical Details
- Python 3.8+ compatibility
- QScintilla for advanced text editing
- lxml for XML parsing and validation
- Qt6 for cross-platform GUI
- Native file dialogs
- Platform-appropriate shortcuts
- Settings persistence with QSettings

## Future Plans

### Version 1.1.0 (Planned)
- Application icon
- Multiple document tabs
- XML Schema generation from XML
- Enhanced find/replace with regex
- Custom XML snippets
- More sample files

### Version 1.2.0 (Planned)
- JSON to XML conversion
- XML diff and merge tools
- Namespace management
- XML catalog support
- Plugin system
- Custom themes

### Version 2.0.0 (Planned)
- Visual schema designer
- XSLT debugger
- Project management
- Git integration
- XML digital signatures
- Database import/export

## Contributing

Contributions are welcome! Please see the README for guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
