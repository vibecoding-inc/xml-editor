# XQuery Panel Implementation Summary

## Overview
This document describes the implementation of the XQuery panel feature added to the XML Editor application.

## Problem Statement
Add a XQuery panel with:
- A code editor linked to a file with auto-save
- File picker to select XQuery files
- XQuery execution engine
- Result display in bottom half of panel
- Use currently open XML file as query context

## Solution

### Architecture
- **XQuery Panel** (`xmleditor/xquery_panel.py`): Main panel widget
  - `XQueryEditor`: Custom QScintilla-based editor with theme support
  - `XQueryPanel`: Main panel with split view (editor + results)
- **XQuery Execution** (`xmleditor/xml_utils.py`): Added `execute_xquery()` method
- **Integration** (`xmleditor/main_window.py`): Dock widget, menu actions, shortcuts

### Key Features

#### File Management
- Browse for existing `.xq` or `.xquery` files
- Create new XQuery files
- File path display
- Auto-save: 1 second after typing stops
- External change detection via `QFileSystemWatcher`
- Prompt to reload when file changes externally

#### XQuery Support (via elementpath)
- XPath 3.0 expressions
- Basic FLWOR expressions (`for...return`)
- Predicates and filters
- Functions: `count()`, `sum()`, `max()`, `min()`, `string-join()`, etc.
- Text extraction
- Attribute access

#### User Interface
- Split view: Query editor (top) / Results (bottom)
- Theme-aware colors for success/error messages
- Formatted result display
- Result count indication
- Clear error reporting

#### Integration
- Dock widget on right side (default hidden)
- **XML Menu**: "XQuery..." action with Ctrl+Shift+Q
- **View Menu**: "Toggle XQuery Panel" action
- **Toolbar**: "XQuery" button
- Automatic query context from active XML tab

### Dependencies
- **elementpath>=5.0.0**: Provides XPath 3.0 / XQuery support

### Testing
- `test_xquery.py`: Comprehensive unit tests
  - Path expressions
  - Predicates
  - FLWOR expressions
  - Built-in functions
  - Text extraction
  - All tests passing

### Documentation
- `FEATURES.md`: Feature description and capabilities
- `USER_GUIDE.md`: Usage instructions with examples
- `README.md`: Feature mention in overview

### Code Quality
- No security vulnerabilities (CodeQL clean)
- All code review issues resolved
- Proper theme integration
- Optimized file watching
- No hardcoded colors

## Implementation Details

### XQuery Execution
```python
# Uses elementpath's XPath30Parser
from elementpath.xpath30 import XPath30Parser
import elementpath

parser = XPath30Parser()
query = parser.parse(xquery_string)
context = elementpath.XPathContext(tree)
result = query.evaluate(context=context)
```

### File Auto-Save Pattern
```python
# Timer-based auto-save
self.save_timer = QTimer()
self.save_timer.setSingleShot(True)
self.save_timer.timeout.connect(self.save_file)
self.save_delay = 1000  # 1 second

# Restart timer on text change
def on_text_changed(self):
    if self.xquery_file_path:
        self.save_timer.start(self.save_delay)
```

### Theme Application
```python
theme = ThemeManager.get_theme(theme_type)
self.setPaper(QColor(theme.get_color("base")))
self.setColor(QColor(theme.get_color("text")))
# ... apply other colors similarly
```

### File Watcher Pattern
```python
# Watch file for external changes
self.file_watcher = QFileSystemWatcher()
self.file_watcher.fileChanged.connect(self.on_file_changed)
self.file_watcher.addPath(file_path)

# Remove with exception handling
try:
    self.file_watcher.removePath(old_path)
except:
    pass  # Path may not be watched
```

## Example Queries

### Basic Paths
```xquery
// All book titles
//book/title

// Title text only
//book/title/text()
```

### Predicates
```xquery
// Books with price > 30
//book[price > 30]/title/text()

// Books by category
//book[@category='cooking']/title
```

### FLWOR Expressions
```xquery
// Return all titles
for $b in //book return $b/title/text()
```

### Functions
```xquery
// Count books
count(//book)

// Maximum price
max(//book/price)

// Join authors
string-join(//book/author/text(), ', ')
```

### XQuery Syntax with Preprocessing
The following XQuery syntax is automatically converted to valid XPath 3.0:

```xquery
(: Example XQuery with version declaration and comments :)
xquery version "1.0";
<Result>{
  for $s in doc("data.xml")/path/to/element
  return
    <Item> {$s/text()} </Item>,
  let $k := count(doc("data.xml")/path/to/element)
  return
    <Count> {$k} </Count>
}</Result>
```

This is automatically preprocessed to:
```xquery
(for $s in /path/to/element return $s/text(), count(/path/to/element))
```

## XQuery Syntax Preprocessing (Production-Ready)
The system includes comprehensive, production-ready preprocessing that automatically converts XQuery syntax to XPath 3.0:

### Declarations and Comments
- **XQuery version declarations** (`xquery version "1.0";`, with optional encoding) are removed
- **Namespace declarations** (`declare namespace ...`) are stripped
- **XQuery comments** (`(: comment :)`) with support for colons inside comments
- **Pragmas** (`(# pragma #)`) are removed
- **Other declare statements** (boundary-space, ordering, etc.) are removed

### Document Functions
- **doc() function** calls are replaced with direct path references
- **doc-available()** returns `true()` (assumes documents are available)
- **collection()** returns empty sequence `()`

### FLWOR Expressions
- **for...return** - fully supported
- **for...where...return** - `where` converted to predicate filters
- **for...let...return** - `let` variables substituted inline
- **for...let...where...return** - combined support with both let and where
- **Multiple conditions** in where clauses with `and`/`or`
- **Comma-separated** FLWOR sequences (e.g., `for...return..., let...return...`)

### Element Construction
- **Direct constructors** (`<tag>{expr}</tag>`) converted to text output
- **Nested element construction** in FLWOR expressions
- **Outer wrapper elements** removed when they wrap entire query

### Path Expression Handling
- **Attribute access** in where clauses: `$var/@attr` → `@attr`
- **Child paths** in where clauses: `$var/child` → `./child`
- **Variable references** with word boundary matching to avoid partial matches

## Supported XQuery Patterns
```xquery
-- Version declarations (automatically removed)
xquery version "1.0" encoding "UTF-8";

-- Namespace declarations (automatically removed)
declare namespace ex = "http://example.com";

-- Comments (automatically removed)
(: This is a comment with : colons :)

-- FLWOR with where
for $book in //book
where $book/@price > 30
return $book/title/text()

-- FLWOR with let
for $book in //book
let $discount := $book/@price * 0.1
return concat($book/title/text(), ' - Discount: $', $discount)

-- FLWOR with let and where
for $book in //book
let $price := $book/@price
where $price > 30 and $book/year = 2003
return $book/title/text()

-- Multiple conditions
for $item in //item
where $item/@status = 'active' and $item/quantity > 0
return $item/name/text()

-- Element construction
for $book in //book
where $book/@category = 'web'
return <WebBook>{$book/title/text()}</WebBook>

-- With doc() function (automatically converted)
for $s in doc("data.xml")/path/to/element
return $s/text()
```

## Limitations
- XPath 3.0 support only (not full XQuery 3.0)
- No `order by` in FLWOR (sorting not supported)
- No `group by` in FLWOR
- No user-defined functions or modules
- No schema-aware processing
- Element construction returns text output
- No typeswitch expressions
- Collection() function returns empty sequence

## Future Enhancements
- Consider full XQuery 3.0 processor (e.g., Saxon/HE)
- Add query history
- Support for query variables
- Query result export
- Syntax highlighting for XQuery
- Auto-completion for XPath functions

## Files Modified
- `xmleditor/xquery_panel.py` (NEW): XQuery panel implementation
- `xmleditor/xml_utils.py`: Added `execute_xquery()` method
- `xmleditor/main_window.py`: Integration (dock widget, menu, toolbar)
- `requirements.txt`: Added elementpath
- `pyproject.toml`: Added elementpath dependency
- `FEATURES.md`: Documentation
- `USER_GUIDE.md`: Usage instructions
- `README.md`: Feature mention
- `test_xquery.py` (NEW): Test suite

## Keyboard Shortcuts
- **Ctrl+Shift+Q**: Toggle XQuery panel

## Conclusion
The XQuery panel provides a powerful tool for querying XML documents with persistent, file-based queries. The implementation follows the application's patterns for panels, themes, and file management, ensuring consistency with existing features.
