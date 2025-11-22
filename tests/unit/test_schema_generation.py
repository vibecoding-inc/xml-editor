#!/usr/bin/env python3
"""
Unit tests for schema generation functionality.
Tests XSD and DTD schema generation from XML documents.
"""

import unittest
from xmleditor.xml_utils import XMLUtilities


class TestXSDGeneration(unittest.TestCase):
    """Test XSD schema generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.books_xml = """<?xml version="1.0" encoding="UTF-8"?>
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
</bookstore>"""
        
        self.employees_xml = """<?xml version="1.0" encoding="UTF-8"?>
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
        
        self.simple_xml = """<?xml version="1.0" encoding="UTF-8"?>
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
    
    def test_xsd_generation_books(self):
        """Test XSD generation for books XML."""
        xsd = XMLUtilities.generate_xsd_schema(self.books_xml)
        self.assertIsNotNone(xsd, "XSD should be generated")
        # Verify it's valid XML
        XMLUtilities.parse_xml(xsd)
    
    def test_xsd_generation_employees(self):
        """Test XSD generation for employees XML."""
        xsd = XMLUtilities.generate_xsd_schema(self.employees_xml)
        self.assertIsNotNone(xsd, "XSD should be generated")
        # Verify it's valid XML
        XMLUtilities.parse_xml(xsd)
    
    def test_xsd_generation_simple(self):
        """Test XSD generation for simple XML."""
        xsd = XMLUtilities.generate_xsd_schema(self.simple_xml)
        self.assertIsNotNone(xsd, "XSD should be generated")
        # Verify it's valid XML
        XMLUtilities.parse_xml(xsd)


class TestDTDGeneration(unittest.TestCase):
    """Test DTD schema generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.books_xml = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
</bookstore>"""
        
        self.employees_xml = """<?xml version="1.0" encoding="UTF-8"?>
<employees>
    <employee id="001">
        <firstName>John</firstName>
        <lastName>Doe</lastName>
        <email>john.doe@example.com</email>
    </employee>
</employees>"""
        
        self.simple_xml = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <item id="1">
        <name>Item One</name>
        <value>100</value>
    </item>
</root>"""
    
    def test_dtd_generation_books(self):
        """Test DTD generation for books XML."""
        dtd = XMLUtilities.generate_dtd_schema(self.books_xml)
        self.assertIsNotNone(dtd, "DTD should be generated")
        self.assertIn("<!ELEMENT bookstore", dtd, "DTD should define bookstore element")
        self.assertIn("<!ELEMENT book", dtd, "DTD should define book element")
        self.assertIn("<!ELEMENT title", dtd, "DTD should define title element")
    
    def test_dtd_generation_employees(self):
        """Test DTD generation for employees XML."""
        dtd = XMLUtilities.generate_dtd_schema(self.employees_xml)
        self.assertIsNotNone(dtd, "DTD should be generated")
        self.assertIn("<!ELEMENT employees", dtd, "DTD should define employees element")
        self.assertIn("<!ELEMENT employee", dtd, "DTD should define employee element")
        self.assertIn("<!ATTLIST employee", dtd, "DTD should define employee attributes")
    
    def test_dtd_generation_simple(self):
        """Test DTD generation for simple XML."""
        dtd = XMLUtilities.generate_dtd_schema(self.simple_xml)
        self.assertIsNotNone(dtd, "DTD should be generated")
        self.assertIn("<!ELEMENT root", dtd, "DTD should define root element")
        self.assertIn("<!ELEMENT item", dtd, "DTD should define item element")


class TestRepeatingElements(unittest.TestCase):
    """Test detection of repeating elements in schema generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.xml_with_repeating = """<?xml version="1.0" encoding="UTF-8"?>
<library>
    <book>Book 1</book>
    <book>Book 2</book>
    <book>Book 3</book>
</library>"""
    
    def test_xsd_repeating_elements(self):
        """Test that XSD correctly identifies repeating elements."""
        xsd = XMLUtilities.generate_xsd_schema(self.xml_with_repeating)
        self.assertIn('maxOccurs="unbounded"', xsd, 
                      "Repeating elements should have maxOccurs='unbounded'")
    
    def test_dtd_repeating_elements(self):
        """Test that DTD correctly identifies repeating elements."""
        dtd = XMLUtilities.generate_dtd_schema(self.xml_with_repeating)
        # DTD uses + or * for repeating elements
        self.assertTrue("book+" in dtd or "book*" in dtd,
                        "Repeating elements should be marked with + or * quantifier")


class TestDataTypeInference(unittest.TestCase):
    """Test data type inference in schema generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.xml_with_types = """<?xml version="1.0" encoding="UTF-8"?>
<data>
    <intValue>42</intValue>
    <decimalValue>3.14</decimalValue>
    <stringValue>Hello World</stringValue>
</data>"""
    
    def test_xsd_type_inference(self):
        """Test that XSD infers data types correctly."""
        xsd = XMLUtilities.generate_xsd_schema(self.xml_with_types)
        # Check that integer type is inferred
        self.assertTrue('xs:integer' in xsd or 'integer' in xsd,
                        "Integer type should be inferred")


if __name__ == '__main__':
    unittest.main()
