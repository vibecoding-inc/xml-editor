#!/usr/bin/env python3
"""
Test script for XQuery functionality.
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
        ("//book/title/text()", "Select all book title text"),
        ("//book[price > 30]/title/text()", "Books with price > 30"),
        ("for $b in //book return $b/title/text()", "FLWOR: all titles"),
        ("count(//book)", "Count all books"),
        ("//book[@category='cooking']/title/text()", "Books in cooking category"),
        ("string-join(//book/author/text(), ', ')", "Join all authors"),
        ("max(//book/price)", "Maximum book price"),
        ("//book[year = 2005]/title", "Books from 2005"),
    ]
    
    print("Testing XQuery Execution")
    print("=" * 80)
    
    for query, description in test_queries:
        print(f"\nTest: {description}")
        print(f"Query: {query}")
        print("-" * 80)
        
        success, message, results, metadata = XMLUtilities.execute_xquery(xml_content, query)
        
        if success:
            print(f"✓ {message}")
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  Result {i}: {result.strip() if isinstance(result, str) else result}")
        else:
            print(f"✗ Error: {message}")
    
    print("\n" + "=" * 80)
    print("XQuery testing complete!")

if __name__ == "__main__":
    test_xquery()
