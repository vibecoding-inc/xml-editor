# Features Documentation

## Complete Feature List

### Core XML Editing

#### Syntax Highlighting
- **XML Lexer**: Professional XML syntax highlighting using QScintilla
- **Color Coding**:
  - Element tags (blue)
  - Attribute names (red)
  - Attribute values (green)
  - Comments (gray)
  - CDATA sections (purple)
  - Text content (black)

#### Editor Features
- **Line Numbers**: Always visible with customizable width
- **Code Folding**: Collapse/expand XML elements
- **Brace Matching**: Highlights matching opening/closing tags
- **Auto-Indentation**: Smart indentation when pressing Enter
- **Indentation Guides**: Visual guides showing indent levels
- **Current Line Highlight**: Highlighted background for active line
- **Edge Marker**: Visual column guide at 80 characters
- **UTF-8 Support**: Full Unicode support for international content
- **Undo/Redo**: Unlimited undo/redo history
- **Auto-Completion**: Context-aware code completion

### File Operations

#### Basic File Management
- **New Document**: Create new XML with template
- **Open File**: Open any XML file
- **Save**: Save current document
- **Save As**: Save with new name/location
- **Auto Save**: Automatically save files every 30 seconds
  - Checkbox in File menu to enable/disable
  - Only saves files with known paths (not "Untitled" documents)
  - Saves all modified open files
  - Preference persists across sessions
- **Recent Files**: Quick access to last 10 opened files
- **Auto-Save Settings**: Window state and preferences saved

#### File Format Support
- **.xml** - XML documents
- **.xsd** - XML Schema files
- **.xsl/.xslt** - XSLT stylesheets
- **.dtd** - Document Type Definitions
- **Any text file** - Can open any text-based file

### XML Validation

#### Well-Formedness Check
- **Instant Validation**: Check if XML is syntactically correct
- **Error Reporting**: Line numbers and error descriptions
- **Real-time Feedback**: Visual indication of validity

#### XSD Schema Validation
- **Dual Input Methods**:
  - **Text Input Tab**: Paste schema directly or load once from file
  - **File Path Tab**: Select schema file with automatic reload on each validation
- **Auto-Reload Feature**: Schema file is reloaded from disk on every validation
  - Perfect for editing schemas and validating XML simultaneously
  - No need to manually reload when schema changes
  - Works seamlessly with multi-tab editing
- **Detailed Validation**: Element and attribute checking
- **Error Details**: Line numbers and specific violations
- **Schema Support**:
  - Simple types
  - Complex types
  - Attributes
  - Elements
  - Sequences
  - Choices
  - Restrictions
  - Extensions

#### DTD Validation
- **Dual Input Methods**:
  - **Text Input Tab**: Paste DTD directly or load once from file
  - **File Path Tab**: Select DTD file with automatic reload on each validation
- **Auto-Reload Feature**: DTD file is reloaded from disk on every validation
- **DTD Support**: Validate against Document Type Definitions
- **External DTD**: Load DTD from file
- **Internal DTD**: Support for embedded DTD
- **Error Reporting**: Detailed validation messages

### XPath Support

#### XPath Query Execution
- **XPath 1.0**: Full XPath 1.0 specification support
- **Query Editor**: Dedicated dialog with examples
- **Result Display**: Formatted results view
- **Query Types**:
  - Element selection
  - Attribute selection
  - Text content extraction
  - Predicates and filters
  - Functions (count, sum, etc.)
  - Position-based selection

#### Example Queries
```xpath
//element                    - All elements
//element[@attr='value']     - Filter by attribute
//element/child              - Direct children
//element//descendant        - All descendants
//element[position()=1]      - First element
count(//element)             - Count elements
//element[text()='value']    - Filter by text
//element[number>10]         - Numeric comparison
```

### XSLT Transformation

#### XSLT 1.0 Support
- **Transform XML**: Apply XSLT stylesheets
- **Load Stylesheet**: From file or paste
- **Result Preview**: View transformed output
- **Save Result**: Export transformation result
- **Apply to Editor**: Replace current content

#### Transformation Features
- **Templates**: Template matching and application
- **Variables**: XSLT variables and parameters
- **Functions**: Built-in XSLT functions
- **Control Flow**: for-each, if, choose
- **Output Methods**: XML, HTML, text
- **Error Handling**: Detailed transformation errors

### XML Tree View

#### Structure Visualization
- **Hierarchical View**: Tree representation of XML structure
- **Node Information**:
  - Element names
  - Text content (truncated)
  - Attributes with values
  - Child count indication

#### Tree Features
- **Expand/Collapse**: Control visibility of branches
- **Alternating Colors**: Easy row identification
- **Tooltips**: Full content on hover
- **Auto-Refresh**: Option to refresh on changes
- **Search**: Find elements in tree

### XML Formatting

#### Pretty-Print
- **Auto-Format**: Properly indent XML
- **Configurable Indent**: Customize indentation (default: 2 spaces)
- **Line Breaks**: Proper line breaks for readability
- **Declaration Preservation**: Keeps XML declaration
- **Encoding Support**: Maintains encoding specification

#### Format Options
- **Indent Size**: Configurable spacing
- **Line Endings**: Unix (LF) or Windows (CRLF)
- **Blank Line Removal**: Cleans up extra whitespace

### Find and Replace

#### Search Functionality
- **Find Text**: Search forward/backward
- **Case Sensitive**: Optional case sensitivity
- **Whole Words**: Match whole words only
- **Wrap Around**: Continue from beginning
- **Regular Expression**: Pattern matching support

#### Replace Operations
- **Replace**: Replace found text
- **Replace All**: Replace all occurrences
- **Preview**: See changes before applying
- **Undo Support**: Revert replacements

### Comment Operations

#### XML Comments
- **Toggle Comment**: Comment/uncomment selection
- **Line Comment**: Comment current line
- **Block Comment**: Comment multiple lines
- **Smart Uncomment**: Remove comment markers

### User Interface

#### Main Window
- **Menu Bar**: Organized by function
- **Toolbar**: Quick access to common operations
- **Status Bar**: Current file and status information
- **Dock Panels**: Movable and closable panels

#### Panels
- **Editor Panel**: Main XML editing area
- **Tree View Panel**: Structure visualization
- **Output Panel**: Errors and messages
- **Resizable Splitters**: Adjust panel sizes

#### Themes and Styling
- **Modern Color Schemes**: Catppuccin theme family for enhanced readability
- **System Theme Detection**: Automatically adapts to system dark/light mode
- **Multiple Theme Options**: 
  - System (Auto) - Detects and applies appropriate theme
  - Catppuccin Latte - Light, warm theme for daytime
  - Catppuccin Frappé - Soft dark theme with muted colors
  - Catppuccin Macchiato - Medium dark theme with vibrant accents
  - Catppuccin Mocha - Deep dark theme for low-light environments
- **Consistent Theming**: All UI elements follow theme colors
- **Persistent Preference**: Theme choice saved across sessions
- **Font**: Monospace font for code (Courier New)
- **Customizable**: Font size and family

### Keyboard Shortcuts

#### File Operations
- Ctrl+N - New file
- Ctrl+O - Open file
- Ctrl+S - Save
- Ctrl+Shift+S - Save As
- Ctrl+Q - Quit

#### Edit Operations
- Ctrl+Z - Undo
- Ctrl+Y - Redo
- Ctrl+X - Cut
- Ctrl+C - Copy
- Ctrl+V - Paste
- Ctrl+F - Find
- Ctrl+H - Replace
- Ctrl+/ - Comment/Uncomment

#### XML Operations
- Ctrl+Shift+F - Format XML
- Ctrl+Shift+V - Validate
- Ctrl+Shift+X - XPath Query
- Ctrl+Shift+T - XSLT Transform

#### View Operations
- Ctrl+T - Toggle Tree View
- Ctrl+O - Toggle Output Panel
- F5 - Refresh Tree

### Settings and Preferences

#### Persistent Settings
- **Window Geometry**: Position and size
- **Panel States**: Visibility and layout
- **Recent Files**: File history
- **Last Directory**: Remember last opened location

#### Customization
- **Editor Font**: Change font and size
- **Word Wrap**: Enable/disable wrapping
- **Indentation**: Spaces or tabs
- **Theme**: Choose from multiple Catppuccin themes or use system auto-detect

### Cross-Platform Support

#### Platform Compatibility
- **Windows**: 10, 11
- **macOS**: 10.14+
- **Linux**: Ubuntu 20.04+, Fedora 33+, etc.

#### Platform Features
- **Native Look**: Uses platform theme
- **File Dialogs**: Native file dialogs
- **Shortcuts**: Platform-appropriate shortcuts
- **Packaging**: Easy distribution methods

### Error Handling

#### User-Friendly Errors
- **Dialog Messages**: Clear error descriptions
- **Output Panel**: Detailed error logs
- **Line Numbers**: Error locations
- **Recovery**: Graceful error recovery

#### Validation Feedback
- **Color Coding**: Red for errors, green for success
- **Detailed Messages**: What went wrong and where
- **Suggestions**: Hints for fixing issues

### Performance

#### Optimization
- **Lazy Loading**: Tree view loads on demand
- **Efficient Parsing**: lxml for fast XML processing
- **Minimal Redraws**: Only update when needed
- **Memory Management**: Proper resource cleanup

#### Large File Support
- **Streaming**: Handle large files
- **Progressive Loading**: Load in chunks
- **Responsive UI**: Non-blocking operations

### Extensibility

#### Architecture
- **Modular Design**: Separate components
- **Plugin Ready**: Easy to extend
- **Custom Validators**: Add new validation types
- **Custom Transformers**: Add new transforms

### Documentation

#### Help Resources
- **README**: Overview and quick start
- **User Guide**: Detailed usage instructions
- **Installation Guide**: Platform-specific setup
- **Sample Files**: Example XML documents
- **API Documentation**: For developers

### Future Features (Roadmap)

#### Planned Enhancements
- XML Schema generation from XML
- JSON to XML conversion
- XML diff and merge tools
- Custom XML snippets
- XML catalog support
- Namespace management
- XML digital signatures
- More XSLT debugging features
- Plugin system
- Macro recording
- Multiple file tabs
- Project management
- Git integration

## Feature Comparison

### vs. XMLSpy
| Feature | XML Editor | XMLSpy |
|---------|-----------|---------|
| Price | Free | Commercial |
| Open Source | Yes | No |
| Cross-Platform | Yes | Windows Only |
| XML Editing | ✓ | ✓ |
| Syntax Highlighting | ✓ | ✓ |
| XSD Validation | ✓ | ✓ |
| DTD Validation | ✓ | ✓ |
| XPath | ✓ | ✓ |
| XSLT | ✓ | ✓ |
| Tree View | ✓ | ✓ |
| Visual Schema Designer | - | ✓ |
| Database Support | - | ✓ |
| WSDL Support | - | ✓ |

### vs. Oxygen XML
| Feature | XML Editor | Oxygen |
|---------|-----------|---------|
| Price | Free | Commercial |
| Learning Curve | Easy | Moderate |
| File Size | ~20KB | ~500MB |
| Startup Time | Instant | Slow |
| Basic XML Features | ✓ | ✓ |
| Advanced Features | Basic | Extensive |

### vs. Notepad++ (XML Plugin)
| Feature | XML Editor | Notepad++ |
|---------|-----------|---------|
| XML Specific | Yes | Plugin |
| XPath Support | Built-in | Limited |
| Schema Validation | Full | Basic |
| Tree View | Native | Plugin |
| Cross-Platform | Yes | Windows Only |
| XSLT | Built-in | No |
