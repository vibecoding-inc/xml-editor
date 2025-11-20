#!/usr/bin/env python3
"""
Test script to verify schema generation functionality.
"""

from xmleditor.xml_utils import XMLUtilities

# Test XML content - books example
books_xml = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
        <description>A comprehensive guide to XML technologies</description>
    </book>
    <book category="cooking">
        <title lang="en">Everyday Italian</title>
        <author>Giada De Laurentiis</author>
        <year>2005</year>
        <price>30.00</price>
        <description>Delicious Italian recipes for everyday cooking</description>
    </book>
    <book category="children">
        <title lang="en">Harry Potter</title>
        <author>J.K. Rowling</author>
        <year>2005</year>
        <price>29.99</price>
        <description>The magical world of Harry Potter</description>
    </book>
    <book category="web">
        <title lang="en">XQuery Kick Start</title>
        <author>James McGovern</author>
        <author>Per Bothner</author>
        <author>Kurt Cagle</author>
        <author>James Linn</author>
        <author>Vaidyanathan Nagarajan</author>
        <year>2003</year>
        <price>49.99</price>
        <description>XQuery fundamentals and practical examples</description>
    </book>
</bookstore>"""

# Test XML content - employees example
employees_xml = """<?xml version="1.0" encoding="UTF-8"?>
<employees>
    <employee id="001">
        <firstName>John</firstName>
        <lastName>Doe</lastName>
        <email>john.doe@example.com</email>
        <department>Engineering</department>
        <salary currency="USD">75000</salary>
        <hireDate>2020-01-15</hireDate>
    </employee>
    <employee id="002">
        <firstName>Jane</firstName>
        <lastName>Smith</lastName>
        <email>jane.smith@example.com</email>
        <department>Marketing</department>
        <salary currency="USD">65000</salary>
        <hireDate>2019-06-01</hireDate>
    </employee>
</employees>"""

# Simple XML for testing
simple_xml = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <item id="1">
        <name>Item One</name>
        <value>100</value>
    </item>
    <item id="2">
        <name>Item Two</name>
        <value>200</value>
    </item>
</root>"""

def test_xsd_generation():
    """Test XSD schema generation."""
    print("Testing XSD schema generation...")
    print("=" * 60)
    
    # Test with books XML
    print("\n1. Generating XSD for books.xml:")
    print("-" * 60)
    try:
        xsd = XMLUtilities.generate_xsd_schema(books_xml)
        print(xsd)
        # Verify it's valid XML
        XMLUtilities.parse_xml(xsd)
        print("✓ Generated XSD is valid XML")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    
    # Test with employees XML
    print("\n2. Generating XSD for employees.xml:")
    print("-" * 60)
    try:
        xsd = XMLUtilities.generate_xsd_schema(employees_xml)
        print(xsd)
        XMLUtilities.parse_xml(xsd)
        print("✓ Generated XSD is valid XML")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    
    # Test with simple XML
    print("\n3. Generating XSD for simple.xml:")
    print("-" * 60)
    try:
        xsd = XMLUtilities.generate_xsd_schema(simple_xml)
        print(xsd)
        XMLUtilities.parse_xml(xsd)
        print("✓ Generated XSD is valid XML")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

def test_dtd_generation():
    """Test DTD schema generation."""
    print("\n\nTesting DTD schema generation...")
    print("=" * 60)
    
    # Test with books XML
    print("\n1. Generating DTD for books.xml:")
    print("-" * 60)
    try:
        dtd = XMLUtilities.generate_dtd_schema(books_xml)
        print(dtd)
        assert "<!ELEMENT bookstore" in dtd
        assert "<!ELEMENT book" in dtd
        assert "<!ELEMENT title" in dtd
        print("✓ Generated DTD contains expected elements")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    
    # Test with employees XML
    print("\n2. Generating DTD for employees.xml:")
    print("-" * 60)
    try:
        dtd = XMLUtilities.generate_dtd_schema(employees_xml)
        print(dtd)
        assert "<!ELEMENT employees" in dtd
        assert "<!ELEMENT employee" in dtd
        assert "<!ATTLIST employee" in dtd
        print("✓ Generated DTD contains expected elements and attributes")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    
    # Test with simple XML
    print("\n3. Generating DTD for simple.xml:")
    print("-" * 60)
    try:
        dtd = XMLUtilities.generate_dtd_schema(simple_xml)
        print(dtd)
        assert "<!ELEMENT root" in dtd
        assert "<!ELEMENT item" in dtd
        print("✓ Generated DTD contains expected elements")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

def test_repeating_elements():
    """Test that repeating elements are detected correctly."""
    print("\n\nTesting repeating element detection...")
    print("=" * 60)
    
    xml_with_repeating = """<?xml version="1.0" encoding="UTF-8"?>
<library>
    <book>Book 1</book>
    <book>Book 2</book>
    <book>Book 3</book>
</library>"""
    
    try:
        xsd = XMLUtilities.generate_xsd_schema(xml_with_repeating)
        print(xsd)
        assert 'maxOccurs="unbounded"' in xsd
        print("✓ Repeating elements detected with maxOccurs='unbounded'")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    
    try:
        dtd = XMLUtilities.generate_dtd_schema(xml_with_repeating)
        print(dtd)
        assert "book+" in dtd or "book*" in dtd
        print("✓ Repeating elements detected in DTD with + or * quantifier")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

def test_data_type_inference():
    """Test that data types are inferred correctly."""
    print("\n\nTesting data type inference...")
    print("=" * 60)
    
    xml_with_types = """<?xml version="1.0" encoding="UTF-8"?>
<data>
    <intValue>42</intValue>
    <decimalValue>3.14</decimalValue>
    <stringValue>Hello World</stringValue>
</data>"""
    
    try:
        xsd = XMLUtilities.generate_xsd_schema(xml_with_types)
        print(xsd)
        # Check that integer and decimal types are inferred
        assert 'xs:integer' in xsd or 'integer' in xsd
        print("✓ Data types inferred correctly")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("XML Schema Generation - Functionality Tests")
    print("=" * 60)
    
    try:
        test_xsd_generation()
        test_dtd_generation()
        test_repeating_elements()
        test_data_type_inference()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\n\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
