# Sample XML Files

This directory contains sample XML files to demonstrate the XML Editor's features.

## Files

### books.xml
A sample bookstore catalog with books, authors, prices, and descriptions.

**Example XPath queries:**
- `//book[@category='web']` - Find all web-related books
- `//book/title/text()` - Get all book titles
- `//book[price>30]` - Find books priced over $30
- `count(//book)` - Count total number of books
- `//book/author` - Get all authors

### books.xsd
XML Schema definition for the books.xml file. Use this to validate the XML structure.

### books_to_html.xsl
XSLT stylesheet that transforms books.xml into an HTML page.

**Usage:**
1. Open books.xml
2. Go to XML → XSLT Transform
3. Load books_to_html.xsl
4. Click Transform to see HTML output

### employees.xml
Sample employee data with personal information and department details.

**Example XPath queries:**
- `//employee[@id='001']` - Find employee by ID
- `//employee[department='Engineering']` - Find all engineering employees
- `//employee[salary>70000]` - Find high-earning employees
- `sum(//salary)` - Calculate total salary

### products.xml
Product catalog with specifications and inventory information.

**Example XPath queries:**
- `//product[category='Electronics']` - Find electronic products
- `//product[stock<100]` - Find low-stock items
- `//product/name/text()` - Get all product names
- `//specifications/*` - Get all specification elements

## How to Use

1. Open the XML Editor application
2. File → Open and select any sample file
3. Try the following features:
   - **Format XML**: XML → Format XML (Ctrl+Shift+F)
   - **Validate**: XML → Validate (Ctrl+Shift+V) - use books.xsd for books.xml
   - **XPath**: XML → XPath Query (Ctrl+Shift+X) - try the example queries above
   - **XSLT**: XML → XSLT Transform (Ctrl+Shift+T) - use books_to_html.xsl with books.xml
   - **Tree View**: View the XML structure in the right panel (Ctrl+T to toggle)

## Creating Your Own Samples

The XML Editor supports:
- Any well-formed XML document
- XSD schema validation
- DTD validation
- XPath 1.0 expressions
- XSLT 1.0 transformations

Feel free to create your own XML files and experiment with the features!
