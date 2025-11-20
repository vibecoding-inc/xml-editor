#!/usr/bin/env python3
"""
Test script to verify XML editor functionality.
"""

from xmleditor.xml_utils import XMLUtilities

# Test XML content
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
    <book category="cooking">
        <title lang="en">Everyday Italian</title>
        <author>Giada De Laurentiis</author>
        <year>2005</year>
        <price>30.00</price>
    </book>
</bookstore>"""

xsd_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="bookstore">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="book" maxOccurs="unbounded">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="title">
                                <xs:complexType>
                                    <xs:simpleContent>
                                        <xs:extension base="xs:string">
                                            <xs:attribute name="lang" type="xs:string"/>
                                        </xs:extension>
                                    </xs:simpleContent>
                                </xs:complexType>
                            </xs:element>
                            <xs:element name="author" type="xs:string"/>
                            <xs:element name="year" type="xs:integer"/>
                            <xs:element name="price" type="xs:decimal"/>
                        </xs:sequence>
                        <xs:attribute name="category" type="xs:string"/>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>"""

def test_xml_validation():
    """Test XML validation."""
    print("Testing XML validation...")
    is_valid, message = XMLUtilities.validate_xml(xml_content)
    print(f"  Well-formed: {is_valid}")
    print(f"  Message: {message}\n")
    assert is_valid, "XML should be well-formed"

def test_xsd_validation():
    """Test XSD validation."""
    print("Testing XSD validation...")
    is_valid, message = XMLUtilities.validate_with_xsd(xml_content, xsd_content)
    print(f"  Valid: {is_valid}")
    print(f"  Message: {message}\n")
    assert is_valid, "XML should be valid against XSD"

def test_xpath_query():
    """Test XPath query."""
    print("Testing XPath queries...")
    
    # Query all book titles
    results = XMLUtilities.xpath_query(xml_content, "//book/title/text()")
    print(f"  Book titles: {results}")
    assert len(results) == 2, "Should find 2 book titles"
    
    # Query books with category='web'
    results = XMLUtilities.xpath_query(xml_content, "//book[@category='web']/title/text()")
    print(f"  Web books: {results}")
    assert len(results) == 1, "Should find 1 web book"
    print()

def test_xml_formatting():
    """Test XML formatting."""
    print("Testing XML formatting...")
    unformatted = "<root><child>text</child></root>"
    formatted = XMLUtilities.format_xml(unformatted)
    print(f"  Original: {unformatted}")
    print(f"  Formatted:\n{formatted}\n")
    assert "<child>" in formatted, "Formatted XML should contain child element"

def test_xml_tree_structure():
    """Test XML tree structure."""
    print("Testing XML tree structure...")
    tree = XMLUtilities.get_xml_tree_structure(xml_content)
    print(f"  Root element: {tree[0]['tag']}")
    print(f"  Number of children: {len(tree[0]['children'])}")
    assert tree[0]['tag'] == 'bookstore', "Root should be bookstore"
    assert len(tree[0]['children']) == 2, "Should have 2 book children"
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("XML Editor - Functionality Tests")
    print("=" * 60)
    print()
    
    try:
        test_xml_validation()
        test_xsd_validation()
        test_xpath_query()
        test_xml_formatting()
        test_xml_tree_structure()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
