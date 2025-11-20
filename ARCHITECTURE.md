# Architecture Overview: Tabs and Validation Pane

## Component Structure

```
MainWindow
├── MenuBar
│   ├── File Menu
│   │   ├── New (Ctrl+N) → create_new_document()
│   │   ├── Open (Ctrl+O) → open_file()
│   │   ├── Save (Ctrl+S) → save_file()
│   │   └── Close → closeEvent()
│   ├── Edit Menu
│   │   ├── Undo/Redo → get_current_editor().undo/redo()
│   │   └── Cut/Copy/Paste → get_current_editor().cut/copy/paste()
│   ├── XML Menu
│   │   ├── Format → format_xml()
│   │   ├── Validate → validate_xml()
│   │   ├── XPath → show_xpath_dialog()
│   │   └── XSLT → show_xslt_dialog()
│   └── View Menu
│       ├── Toggle Tree View (Ctrl+T)
│       ├── Toggle Output Panel (Ctrl+O)
│       └── Toggle Validation Panel (Ctrl+Shift+P)
│
├── Central Widget
│   └── Splitter (Horizontal)
│       ├── QTabWidget (70%)
│       │   ├── Tab 0: XMLEditor (file1.xml) ← current_editor
│       │   ├── Tab 1: XMLEditor (schema.xsd)
│       │   └── Tab 2: XMLEditor (file3.xml)
│       │   └── [Connected: tabCloseRequested → close_tab()]
│       │       [Connected: currentChanged → on_tab_changed()]
│       │
│       └── XMLTreeView (30%)
│           └── [Syncs with current tab on switch]
│
├── DockWidget (Bottom): Output Panel
│   └── QTextEdit (Read-only)
│       └── [Shows errors and messages]
│
└── DockWidget (Right): Validation Panel ← NEW!
    └── Validation Widget
        ├── Validation Buttons
        │   ├── [Well-Formed] → validate_well_formed()
        │   ├── [Validate XSD] → validate_with_xsd()
        │   └── [Validate DTD] → validate_with_dtd()
        ├── Schema Input Area
        │   ├── QTextEdit (schema/DTD content)
        │   └── [Load Schema File] → load_schema_file()
        └── Results Display
            └── QTextEdit (Read-only, color-coded)
```

## Data Flow

### Opening a File

```
User clicks "Open" (Ctrl+O)
    ↓
open_file() → QFileDialog
    ↓
load_file(path)
    ↓
Check if already open → if yes, switch to existing tab
    ↓ if no
create_editor_tab(title, content, path)
    ↓
Create XMLEditor instance
    ↓
Add to tab_widget
    ↓
Store in tab_data[index] = {file_path, is_modified: False}
    ↓
Set as current tab
    ↓
Trigger on_tab_changed()
    ↓
Update tree_view and window_title
```

### Validation Workflow

```
User clicks "Validate" (Ctrl+Shift+V)
    ↓
validate_xml()
    ↓
Show validation_dock
    ↓
Call validate_well_formed()
    ↓
Get current_editor content
    ↓
XMLUtilities.validate_xml(content)
    ↓
Display result in validation_result (green/red)
    ↓
User can continue editing without closing panel
    ↓
User loads schema into validation_schema_input
    ↓
User clicks "Validate XSD"
    ↓
validate_with_xsd()
    ↓
Get current_editor content + schema content
    ↓
XMLUtilities.validate_with_xsd(xml, schema)
    ↓
Display result (stays open for continuous editing)
```

### Tab State Management

```
tab_data = {
    0: {
        'file_path': '/home/user/document.xml',
        'is_modified': True
    },
    1: {
        'file_path': '/home/user/schema.xsd',
        'is_modified': False
    },
    2: {
        'file_path': None,  # Unsaved "Untitled"
        'is_modified': True
    }
}

When text changes in Tab 0:
    on_text_changed()
    ↓
    tab_data[0]['is_modified'] = True
    ↓
    update_window_title() → "XML Editor - document.xml *"

When closing Tab 0:
    close_tab(0)
    ↓
    Check tab_data[0]['is_modified']
    ↓
    Prompt: Save / Discard / Cancel
    ↓
    Remove tab from widget
    ↓
    Rebuild tab_data with shifted indices:
        1 → 0
        2 → 1
```

## Key Design Decisions

1. **Independent Editors**: Each tab has its own XMLEditor instance with independent state
   - Benefit: Separate undo/redo history, no cross-contamination
   - Trade-off: Slightly more memory usage

2. **Tab Data Dictionary**: Using integer indices as keys
   - Benefit: Simple lookup, easy to track state
   - Trade-off: Must shift indices when closing tabs

3. **Dockable Validation**: QDockWidget instead of QDialog
   - Benefit: Can stay open, user can position it
   - Trade-off: More complex UI layout

4. **Current Editor Pattern**: get_current_editor() for all operations
   - Benefit: Consistent, reduces errors, easy to maintain
   - Trade-off: Null checks needed everywhere

5. **Duplicate Prevention**: Check existing tabs before opening
   - Benefit: Prevents confusion, conserves resources
   - Trade-off: Linear search through tabs (acceptable for typical use)

## Extension Points

Future features can build on this architecture:

- **Tab Context Menus**: Right-click on tabs → close others, close all, etc.
- **Session Management**: Save tab_data to settings, restore on startup
- **Auto-Validation**: Connect textChanged signal to debounced validation
- **Split View**: Add second tab_widget with synchronized state
- **Tab Groups**: Color-code or group related tabs
- **Quick Switch**: Ctrl+Tab overlay with tab previews
