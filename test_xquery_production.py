#!/usr/bin/env python3
"""
Production XQuery tests using the Saxon/C engine.
"""

from xmleditor.xml_utils import XMLUtilities
from lxml import etree

# Test XML content
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web" price="39.95">
        <title>Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
    </book>
    <book category="cooking" price="30.00">
        <title>Everyday Italian</title>
        <author>Giada De Laurentiis</author>
        <year>2005</year>
    </book>
    <book category="children" price="29.99">
        <title>Harry Potter</title>
        <author>J K. Rowling</author>
        <year>2005</year>
    </book>
    <book category="web" price="49.99">
        <title>XQuery Kick Start</title>
        <author>James McGovern</author>
        <year>2003</year>
    </book>
</bookstore>"""

def test_production_xquery():
    """Validate that rich XQuery expressions return an XML document."""
    query = """
    declare variable $threshold := 35.0;
    <expensive-books>{
        for $b in //book[@price > $threshold]
        return <book title="{ $b/title/text() }" price="{ $b/@price }"/>
    }</expensive-books>
    """
    
    success, message, result_xml = XMLUtilities.execute_xquery(xml_content, query)
    assert success, message
    
    result_tree = etree.fromstring(result_xml.encode('utf-8'))
    books = result_tree.findall('.//result/expensive-books/book')
    
    assert len(books) == 2, "Expected two expensive books in result document"
    titles = sorted([book.get("title") for book in books])
    assert titles == ["Learning XML", "XQuery Kick Start"]

def test_scalar_result_wrapped_in_xml():
    """Ensure scalar XQuery results are wrapped in the XML result document."""
    query = "string-join(//book/title/text(), ', ')"
    success, message, result_xml = XMLUtilities.execute_xquery(xml_content, query)
    assert success, message
    
    result_tree = etree.fromstring(result_xml.encode('utf-8'))
    results = result_tree.findall('./result')
    assert results, "Scalar result should still be wrapped in <result>"
    assert "Learning XML" in results[0].text
    assert "Harry Potter" in results[0].text

if __name__ == "__main__":
    test_production_xquery()
    test_scalar_result_wrapped_in_xml()
    print("\n✓ All production tests passed!")
