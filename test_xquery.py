#!/usr/bin/env python3
"""
Test script for XQuery functionality.
"""

from xmleditor.xml_utils import XMLUtilities
from lxml import etree

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
    <book category="children">
        <title lang="en">Harry Potter</title>
        <author>J K. Rowling</author>
        <year>2005</year>
        <price>29.99</price>
    </book>
</bookstore>"""

def test_xquery():
    """Test various XQuery expressions."""
    
    test_queries = [
        ("//book/title", "Select all book titles"),
        ("count(//book)", "Count all books"),
    ]
    
    print("Testing XQuery Execution")
    print("=" * 80)
    
    for query, description in test_queries:
        print(f"\nTest: {description}")
        print(f"Query: {query}")
        print("-" * 80)
        
        success, message, result_xml = XMLUtilities.execute_xquery(xml_content, query)
        
        assert success, message
        result_tree = etree.fromstring(result_xml.encode('utf-8'))
        fragments = result_tree.findall('./result')
        assert fragments, "Result document should contain at least one <result> element"
        
        print(f"✓ {message}")
        pretty = etree.tostring(result_tree, encoding='unicode', pretty_print=True)
        print(pretty.strip())
        
        if description == "Select all book titles":
            titles = [title for title in fragments[0].xpath('.//title/text()')]
            assert titles == ["Learning XML", "Everyday Italian", "Harry Potter"]
        elif description == "Count all books":
            counts = fragments[0].xpath('text()')
            assert counts and counts[0].strip() == "3"
    
    print("\n" + "=" * 80)
    print("XQuery testing complete!")

if __name__ == "__main__":
    test_xquery()
