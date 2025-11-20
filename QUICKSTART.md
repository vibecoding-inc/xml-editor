# Quick Start Guide

Get started with XML Editor in 5 minutes!

## Installation

```bash
# Install from source
git clone https://github.com/profiluefter/xml-editor.git
cd xml-editor
pip install -r requirements.txt
pip install .
```

## Launch

```bash
xml-editor
```

## Basic Usage

### 1. Create a New XML Document
- Click **File → New** (or press `Ctrl+N`)
- You'll see a template with XML declaration

### 2. Add Your XML Content
```xml
<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title>Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
</bookstore>
```

### 3. Format Your XML
- Click **XML → Format XML** (or press `Ctrl+Shift+F`)
- Your XML will be beautifully indented

### 4. Validate Your XML
- Click **XML → Validate** (or press `Ctrl+Shift+V`)
- Check the "Well-Formedness" tab
- See if your XML is valid ✓

### 5. Try XPath
- Click **XML → XPath Query** (or press `Ctrl+Shift+X`)
- Enter: `//book/title/text()`
- Click **Execute**
- See your book titles!

### 6. View Tree Structure
- Look at the right panel
- See your XML as a tree
- Expand and collapse nodes

### 7. Save Your Work
- Click **File → Save** (or press `Ctrl+S`)
- Choose a location
- Your XML is saved!

## Try Sample Files

```bash
# Open a sample
cd xml-editor/samples
xml-editor books.xml
```

Then try:
1. **Format**: `Ctrl+Shift+F`
2. **XPath**: `Ctrl+Shift+X` → `//book[@category='web']`
3. **Validate**: `Ctrl+Shift+V` → Load `books.xsd`
4. **Transform**: `Ctrl+Shift+T` → Load `books_to_html.xsl`

## Key Shortcuts

| Action | Shortcut |
|--------|----------|
| New | `Ctrl+N` |
| Open | `Ctrl+O` |
| Save | `Ctrl+S` |
| Format | `Ctrl+Shift+F` |
| Validate | `Ctrl+Shift+V` |
| XPath | `Ctrl+Shift+X` |
| XSLT | `Ctrl+Shift+T` |
| Find | `Ctrl+F` |
| Comment | `Ctrl+/` |

## Common Tasks

### Validate Against Schema
1. Open your XML file
2. Press `Ctrl+Shift+V`
3. Go to "XSD Schema" tab
4. Load your .xsd file
5. Click "Validate"

### Transform with XSLT
1. Open your XML file
2. Press `Ctrl+Shift+T`
3. Load your .xsl file
4. Click "Transform"
5. Save or apply result

### Search XML with XPath
1. Open your XML file
2. Press `Ctrl+Shift+X`
3. Enter XPath expression
4. Press Enter or click "Execute"

## Tips

- **Auto-format on paste**: Paste XML, then press `Ctrl+Shift+F`
- **Quick validation**: Changes turn red if invalid
- **Tree navigation**: Click tree nodes to jump in editor
- **Recent files**: File menu shows last 10 files
- **Error details**: Check output panel at bottom for details

## Getting Help

- Press `F1` or click **Help → About**
- Read `USER_GUIDE.md` for detailed instructions
- Check `FEATURES.md` for complete feature list
- Visit [GitHub Issues](https://github.com/profiluefter/xml-editor/issues)

## Next Steps

1. Read the full [User Guide](USER_GUIDE.md)
2. Explore [sample files](samples/)
3. Learn about [all features](FEATURES.md)
4. Check the [installation guide](INSTALL.md) for advanced setup

## Troubleshooting

**Can't start?**
```bash
# Check installation
pip show xml-editor

# Run directly
python -m xmleditor.main
```

**No syntax highlighting?**
- Make sure your file has valid XML structure
- Save file with .xml extension

**Tree view not showing?**
- Press `F5` to refresh
- Check for XML errors

**Need more help?**
- See `USER_GUIDE.md` → Troubleshooting section
- Check GitHub Issues
- Read the documentation

---

**Ready to go? Start editing!**

```bash
xml-editor
```
