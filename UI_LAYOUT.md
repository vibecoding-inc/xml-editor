# Visual UI Layout

## Main Window Layout

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║ XML Editor - document.xml *                                              [_][□][X]║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ File  Edit  XML  View  Help                                                     ║
╟──────────────────────────────────────────────────────────────────────────────────╢
║ [New] [Open] [Save] | [Undo] [Redo] | [Format] [Validate] [XPath]             ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ ┌──────────────────────────────────────────────────┬─────────────────────────┐  ║
║ │ ┌──────────────────────────────────────────────┐ │ Tree View               │  ║
║ │ │ [document.xml *] [schema.xsd] [data.xml]  [+]│ │                         │  ║
║ │ ├──────────────────────────────────────────────┤ │ ■ bookstore             │  ║
║ │ │ <?xml version="1.0"?>                        │ │   ├─ book               │  ║
║ │ │ <bookstore>                                  │ │   │  ├─ title           │  ║
║ │ │   <book category="web">                      │ │   │  ├─ author          │  ║
║ │ │     <title>Learning XML</title>              │ │   │  ├─ year            │  ║
║ │ │     <author>Erik T. Ray</author>             │ │   │  └─ price           │  ║
║ │ │     <year>2003</year>                        │ │   └─ book               │  ║
║ │ │     <price>39.95</price>                     │ │      ├─ title           │  ║
║ │ │   </book>                                    │ │      ├─ author          │  ║
║ │ │   <book category="cooking">                  │ │      ├─ year            │  ║
║ │ │     <title>Everyday Italian</title>          │ │      └─ price           │  ║
║ │ │   </book>                                    │ │                         │  ║
║ │ │ </bookstore>                                 │ │                         │  ║
║ │ └──────────────────────────────────────────────┘ └─────────────────────────┘  ║
║ │                                                                               │  ║
║ │                      EDITOR TABS AREA                                        │  ║
║ │                   (70% of horizontal space)                                  │  ║
║ └───────────────────────────────────────────────────────────────────────────────┘  ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Ready                                                        Line: 5, Col: 10   ║
╚══════════════════════════════════════════════════════════════════════════════════╝

        DOCKABLE PANELS (can be shown/hidden):

┌────────────────────────────────────────┐  ┌────────────────────────────────────┐
│ Output Panel (Bottom)                  │  │ Validation Panel (Right)           │
├────────────────────────────────────────┤  ├────────────────────────────────────┤
│ Format Error:                          │  │ [Well-Formed] [Validate XSD]       │
│ Line 5: Unclosed tag 'book'            │  │ [Validate DTD]                     │
│                                        │  │                                    │
└────────────────────────────────────────┘  │ Schema/DTD Content:                │
                                            │ ┌────────────────────────────────┐ │
                                            │ │ <?xml version="1.0"?>          │ │
                                            │ │ <xs:schema ...>                │ │
                                            │ │   <xs:element name="bookstore">│ │
                                            │ │   ...                          │ │
                                            │ └────────────────────────────────┘ │
                                            │ [Load Schema File]                 │
                                            │                                    │
                                            │ Validation Result:                 │
                                            │ ┌────────────────────────────────┐ │
                                            │ │ ✓ XML is valid against schema  │ │
                                            │ │                                │ │
                                            │ └────────────────────────────────┘ │
                                            └────────────────────────────────────┘
```

## Feature Highlights in UI

### 1. Tab Bar (Top of Editor Area)
```
┌──────────────────────────────────────────────────────────────┐
│ [document.xml *] [X]  [schema.xsd] [X]  [data.xml] [X]  [+] │
│  ↑ Active tab         ↑ Clean tab       ↑ Another tab       │
│    (modified)           (saved)                               │
└──────────────────────────────────────────────────────────────┘
```
- **Active tab**: Highlighted
- **Modified indicator**: Asterisk (*) after filename
- **Close button**: X on each tab
- **Add button**: + to create new tab

### 2. Validation Panel (Dockable, Right Side)
```
╔════════════════════════════════════╗
║ Validation                    [X]  ║  ← Can be closed
╟────────────────────────────────────╢
║ [Well-Formed] [Validate XSD]       ║  ← Quick validation buttons
║ [Validate DTD]                     ║
║                                    ║
║ Schema/DTD Content:                ║  ← Paste or load schema
║ ┌────────────────────────────────┐ ║
║ │                                │ ║
║ │ (Schema content here)          │ ║
║ │                                │ ║
║ └────────────────────────────────┘ ║
║ [Load Schema File]                 ║  ← Browse for .xsd/.dtd
║                                    ║
║ Validation Result:                 ║  ← Results stay visible
║ ┌────────────────────────────────┐ ║
║ │ ✓ XML is well-formed           │ ║  ← Green for success
║ │                                │ ║
║ └────────────────────────────────┘ ║
╚════════════════════════════════════╝
```

## User Interactions

### Opening Multiple Files
```
User Action:           Result:
─────────────          ───────────────────────────────
Click "Open"    →      [Tab1: file1.xml]
Select file.xml        
                       
Click "Open"    →      [Tab1: file1.xml] [Tab2: schema.xsd]
Select schema.xsd      
                       
Click "Open"    →      [Tab1: file1.xml] [Tab2: schema.xsd] [Tab3: data.xml]
Select data.xml        
```

### Working with Validation Panel
```
Workflow:
─────────
1. Open XML file                    → Shows in Tab 1
2. Open XSD file                    → Shows in Tab 2
3. Click View → Validation Panel    → Panel appears on right
4. Click on Tab 2 (schema.xsd)      → Schema content visible
5. Select all, copy                 → Ctrl+A, Ctrl+C
6. Click on validation panel input  → Focus on input area
7. Paste                            → Ctrl+V, schema in panel
8. Click on Tab 1 (XML file)        → Switch back to XML
9. Click "Validate XSD"             → Results appear in panel
10. Edit XML                        → Panel stays open
11. Click "Validate XSD" again      → See updated results
```

### Tab Management
```
Close Tab:                  Save Tab:
──────────                  ─────────
Click X on tab      →       Click Ctrl+S        →
  ↓                           ↓
If modified:                Updates tab title:
"Save changes?"            [file.xml *]  →  [file.xml]
  ↓                                            (no asterisk)
[Save][Discard][Cancel]
  ↓
Tab closes if not cancelled
```

## Keyboard Navigation

```
Ctrl+N           → Create new tab
Ctrl+O           → Open file in new tab
Ctrl+S           → Save current tab
Ctrl+W           → Close current tab
Ctrl+Tab         → Next tab
Ctrl+Shift+Tab   → Previous tab

Ctrl+Shift+V     → Open validation panel and validate
Ctrl+Shift+P     → Toggle validation panel
Ctrl+T           → Toggle tree view
Ctrl+O           → Toggle output panel
```

## State Indicators

```
Window Title:
─────────────
XML Editor - document.xml *        ← Current file, modified
XML Editor - schema.xsd            ← Current file, saved
XML Editor - Untitled *            ← New file, unsaved
XML Editor                         ← No file open (shouldn't happen)

Tab Title:
──────────
document.xml *                     ← Modified
schema.xsd                         ← Saved
Untitled                           ← New, unsaved

Validation Results:
───────────────────
✓ XML is well-formed               ← Green text
✗ Element 'book': Missing child    ← Red text
```

## Layout Flexibility

All panels are dockable and can be:
- **Moved**: Drag panel title bar to different edges
- **Floated**: Drag away from window to create floating panel
- **Hidden**: Click X or use toggle menu items
- **Resized**: Drag splitter bars between panels

This provides maximum flexibility for different workflows and screen sizes.
