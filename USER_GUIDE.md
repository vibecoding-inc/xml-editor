# User Guide

## Getting Started

### First Launch

When you first launch XML Editor, you'll see:
- A blank editor with an XML template
- A tree view panel on the right
- Menu bar with File, Edit, XML, View, and Help menus
- Toolbar with quick access buttons
- Status bar at the bottom

### Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│ File  Edit  XML  View  Help          [Toolbar Buttons] │
├───────────────────────────┬─────────────────────────────┤
│                           │                             │
│   XML Editor              │    Tree View                │
│   (Syntax Highlighting)   │    (XML Structure)          │
│                           │                             │
│                           │                             │
├───────────────────────────┴─────────────────────────────┤
│ Output Panel (Errors/Warnings)                          │
├─────────────────────────────────────────────────────────┤
│ Status Bar                                              │
└─────────────────────────────────────────────────────────┘
```

## Basic Operations

### Creating a New Document

1. **File → New** (or Ctrl+N)
2. A new document with XML declaration is created
3. Start typing your XML content

### Opening an Existing File

1. **File → Open** (or Ctrl+O)
2. Navigate to your XML file
3. The file contents appear in the editor
4. The tree view automatically updates

### Saving Files

- **Save**: File → Save (or Ctrl+S)
  - If file is new, you'll be prompted for a name
  - Existing files are saved directly

- **Save As**: File → Save As (or Ctrl+Shift+S)
  - Save with a new name or location

- **Auto Save**: File → Auto Save
  - Check to enable automatic saving every 30 seconds
  - Only saves files that have been saved before (not "Untitled" documents)
  - Saves all open modified files automatically
  - Status bar shows "Auto-saved X file(s)" when files are saved
  - Your preference is saved and restored when you reopen the application

### Recent Files

- **File → Recent Files** shows your 10 most recent files
- Click any file to open it quickly

## Editing Features

### Basic Editing

- **Undo**: Edit → Undo (or Ctrl+Z)
- **Redo**: Edit → Redo (or Ctrl+Y)
- **Cut**: Edit → Cut (or Ctrl+X)
- **Copy**: Edit → Copy (or Ctrl+C)
- **Paste**: Edit → Paste (or Ctrl+V)

### Find and Replace

1. **Find**: Edit → Find (or Ctrl+F)
   - Enter search text
   - Press Enter to find next occurrence

2. **Replace**: Edit → Replace (or Ctrl+H)
   - Enter text to find
   - Enter replacement text
   - All occurrences are replaced

### Commenting

- **Comment/Uncomment**: Edit → Comment/Uncomment (or Ctrl+/)
  - Select text to comment: wraps in `<!-- -->`
  - Select commented text to uncomment: removes comment markers

## XML Operations

### Formatting XML

**XML → Format XML** (or Ctrl+Shift+F)

Automatically formats and indents your XML:

**Before:**
```xml
<root><child>text</child><child>text2</child></root>
```

**After:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<root>
  <child>text</child>
  <child>text2</child>
</root>
```

### Validating XML

**XML → Validate** (or Ctrl+Shift+V)

Opens validation dialog with three tabs:

1. **Well-Formedness**
   - Checks if XML is syntactically correct
   - Shows errors with line numbers

2. **XSD Schema**
   - Paste or load XSD schema
   - Click Validate to check conformance
   - Shows detailed validation errors

3. **DTD**
   - Paste or load DTD
   - Click Validate to check conformance

### XPath Queries

**XML → XPath Query** (or Ctrl+Shift+X)

Execute XPath expressions to query your XML:

**Example Queries:**
```xpath
//book                          # All book elements
//book[@category='web']         # Books with category='web'
//book/title/text()             # All book titles
//book[price>30]                # Books priced over 30
count(//book)                   # Count books
//book[position()=1]            # First book
//book/author                   # All authors
```

Results appear in the results panel below.

### XSLT Transformations

**XML → XSLT Transform** (or Ctrl+Shift+T)

Apply XSLT stylesheets to transform XML:

1. Open dialog
2. Paste or load XSLT stylesheet
3. Click Transform
4. View transformed output
5. Options:
   - **Save Result**: Save to file
   - **Apply to Editor**: Replace current content

### Tree View

**View → Toggle Tree View** (or Ctrl+T)

The tree view shows:
- XML element hierarchy
- Element names
- Text content (first 50 characters)
- Attributes

Click any element to see its details.

**Refresh Tree**: XML → Refresh Tree View (or F5)

## Advanced Features

### Syntax Highlighting

Automatic color coding for XML elements (colors shown are for default theme):
- **Purple/Mauve**: Element tags
- **Green**: Attribute names
- **Yellow**: Attribute values (strings)
- **Gray**: Comments
- **Pink**: CDATA sections
- **Orange**: Numbers
- **Teal**: Entities (e.g., &amp;)

Note: Actual colors vary based on your selected theme. All Catppuccin themes provide excellent contrast and readability.

### Code Folding

Click the [-] next to an opening tag to collapse it.
Click [+] to expand.

### Line Numbers

Line numbers appear on the left margin for easy reference.

### Brace Matching

When cursor is near a tag, the matching tag is highlighted in light green.

### Auto-Indentation

Press Enter - the next line is automatically indented.

### Word Wrap

**View → Word Wrap**

Toggle word wrapping for long lines.

### Theme Selection

**View → Theme**

Choose from multiple beautiful color schemes:

1. **System (Auto)** - Automatically detects your system's dark/light mode and applies the appropriate theme
2. **Catppuccin Latte** - A light, warm theme perfect for daytime coding
3. **Catppuccin Frappé** - A soft dark theme with muted colors
4. **Catppuccin Macchiato** - A medium dark theme with vibrant accents
5. **Catppuccin Mocha** - A deep dark theme ideal for low-light environments

Your theme preference is automatically saved and restored when you reopen the application.

The themes provide consistent coloring across:
- Editor background and text
- Line numbers and margins
- Syntax highlighting for XML elements
- Selection and matched braces
- All UI components

### Output Panel

**View → Toggle Output Panel** (or Ctrl+O)

Shows:
- Validation errors
- Parsing errors
- Operation results

## Tips and Tricks

### Auto-Save for Safety
Enable auto-save (File → Auto Save) to automatically save your work every 30 seconds. This helps prevent data loss in case of unexpected crashes or power failures.

### Quick Formatting
Select text and press Ctrl+Shift+F to format selection.

### XPath Testing
Use the XPath dialog to test expressions before using them in code.

### Schema Validation Workflow
1. Open XML file
2. Open validation dialog
3. Load XSD schema
4. Keep dialog open
5. Edit XML in main window
6. Re-validate after changes

### XSLT Development
1. Keep XSLT dialog open
2. Edit XSLT in dialog
3. Click Transform to see results
4. Iterate until satisfied

### Keyboard Navigation
- Ctrl+Home: Jump to start
- Ctrl+End: Jump to end
- Ctrl+Right: Next word
- Ctrl+Left: Previous word
- Ctrl+G: Go to line (via QScintilla)

### Multiple Instances
You can open multiple XML Editor windows to work on different files.

## Keyboard Shortcuts Reference

| Action | Shortcut |
|--------|----------|
| New File | Ctrl+N |
| Open File | Ctrl+O |
| Save | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Quit | Ctrl+Q |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Cut | Ctrl+X |
| Copy | Ctrl+C |
| Paste | Ctrl+V |
| Find | Ctrl+F |
| Replace | Ctrl+H |
| Comment/Uncomment | Ctrl+/ |
| Format XML | Ctrl+Shift+F |
| Validate | Ctrl+Shift+V |
| XPath Query | Ctrl+Shift+X |
| XSLT Transform | Ctrl+Shift+T |
| Toggle Tree View | Ctrl+T |
| Toggle Output | Ctrl+O |
| Refresh Tree | F5 |

## Troubleshooting

### Tree view not updating
Press F5 or XML → Refresh Tree View

### Syntax highlighting not working
The lexer requires valid XML structure. Check for errors.

### Can't save file
- Check file permissions
- Ensure directory exists
- Try Save As with different location

### Application won't start
- Verify Python installation
- Check dependencies: `pip install -r requirements.txt`
- Run from command line to see errors

### Slow performance with large files
- Tree view updates can be slow for very large files
- Consider hiding tree view (Ctrl+T) for large documents
- Use XPath to navigate instead of scrolling

## Getting Help

- **Help → About**: Version and feature information
- GitHub Issues: Report bugs or request features
- Documentation: Check README.md for detailed information
