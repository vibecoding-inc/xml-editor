#!/usr/bin/env python3
"""
Unit tests for XML utilities functionality.
Tests validation, XPath queries, formatting, and tree structure operations.
"""

import unittest
from xmleditor.xml_utils import XMLUtilities


class TestXMLValidation(unittest.TestCase):
    """Test XML validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
</bookstore>"""
        
        self.xsd_schema = """<?xml version="1.0" encoding="UTF-8"?>
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
    
    def test_xml_well_formed(self):
        """Test that well-formed XML is validated correctly."""
        is_valid, message = XMLUtilities.validate_xml(self.valid_xml)
        self.assertTrue(is_valid, "XML should be well-formed")
        self.assertIn("well-formed", message.lower())
    
    def test_xml_malformed(self):
        """Test that malformed XML is detected."""
        malformed_xml = "<root><child></root>"  # Missing closing tag for child
        is_valid, message = XMLUtilities.validate_xml(malformed_xml)
        self.assertFalse(is_valid, "Malformed XML should not be valid")
    
    def test_xsd_validation_valid(self):
        """Test XSD validation with valid XML."""
        is_valid, message = XMLUtilities.validate_with_xsd(self.valid_xml, self.xsd_schema)
        self.assertTrue(is_valid, "XML should be valid against XSD")
    
    def test_xsd_validation_invalid(self):
        """Test XSD validation with invalid XML."""
        invalid_xml = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title>Missing lang attribute</title>
    </book>
</bookstore>"""
        is_valid, message = XMLUtilities.validate_with_xsd(invalid_xml, self.xsd_schema)
        self.assertFalse(is_valid, "Invalid XML should not validate against XSD")


class TestXPathQueries(unittest.TestCase):
    """Test XPath query functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.xml_content = """<?xml version="1.0" encoding="UTF-8"?>
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
    
    def test_xpath_query_all_titles(self):
        """Test XPath query to find all book titles."""
        results = XMLUtilities.xpath_query(self.xml_content, "//book/title/text()")
        self.assertEqual(len(results), 2, "Should find 2 book titles")
        self.assertIn("Learning XML", results)
        self.assertIn("Everyday Italian", results)
    
    def test_xpath_query_with_predicate(self):
        """Test XPath query with attribute predicate."""
        results = XMLUtilities.xpath_query(self.xml_content, "//book[@category='web']/title/text()")
        self.assertEqual(len(results), 1, "Should find 1 web book")
        self.assertEqual(results[0], "Learning XML")
    
    def test_xpath_query_empty_result(self):
        """Test XPath query that returns no results."""
        results = XMLUtilities.xpath_query(self.xml_content, "//book[@category='nonexistent']/title/text()")
        self.assertEqual(len(results), 0, "Should find no results for nonexistent category")


class TestXMLFormatting(unittest.TestCase):
    """Test XML formatting functionality."""
    
    def test_format_unformatted_xml(self):
        """Test formatting of unformatted XML."""
        unformatted = "<root><child>text</child></root>"
        formatted = XMLUtilities.format_xml(unformatted)
        self.assertIn("<child>", formatted, "Formatted XML should contain child element")
        self.assertIn("\n", formatted, "Formatted XML should contain newlines")
    
    def test_format_preserves_content(self):
        """Test that formatting preserves content."""
        xml = "<root><child>Important Text</child></root>"
        formatted = XMLUtilities.format_xml(xml)
        self.assertIn("Important Text", formatted, "Formatted XML should preserve text content")
    
    def test_format_with_attributes(self):
        """Test formatting XML with attributes."""
        xml = '<root attr="value"><child>text</child></root>'
        formatted = XMLUtilities.format_xml(xml)
        self.assertIn('attr="value"', formatted, "Formatted XML should preserve attributes")


class TestXMLTreeStructure(unittest.TestCase):
    """Test XML tree structure functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
    </book>
    <book category="cooking">
        <title lang="en">Everyday Italian</title>
        <author>Giada De Laurentiis</author>
    </book>
</bookstore>"""
    
    def test_tree_structure_root_element(self):
        """Test that root element is correctly identified."""
        tree = XMLUtilities.get_xml_tree_structure(self.xml_content)
        self.assertEqual(tree[0]['tag'], 'bookstore', "Root element should be 'bookstore'")
    
    def test_tree_structure_children_count(self):
        """Test that correct number of children is returned."""
        tree = XMLUtilities.get_xml_tree_structure(self.xml_content)
        self.assertEqual(len(tree[0]['children']), 2, "Root should have 2 book children")
    
    def test_tree_structure_nested_elements(self):
        """Test that nested elements are represented correctly."""
        tree = XMLUtilities.get_xml_tree_structure(self.xml_content)
        self.assertIn('children', tree[0], "Root should have children key")
        # Check first book has children
        first_book = tree[0]['children'][0]
        self.assertGreater(len(first_book['children']), 0, "Book should have child elements")


if __name__ == '__main__':
    unittest.main()
