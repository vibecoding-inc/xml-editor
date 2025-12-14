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

def test_element_construction_with_flwor():
    """Element construction with FLWOR and ordering should be preserved."""
    query = """
    xquery version "1.0";
    <h1>A list of books</h1>
    <p>Here are some interesting books:</p>
    <ul>{
      for $b in //book
      order by $b/title
      return <li><i>{ string($b/title) }</i> by { string($b/author) }</li>
    }</ul>
    """
    success, message, result_xml = XMLUtilities.execute_xquery(xml_content, query)
    assert success, message
    
    tree = etree.fromstring(result_xml.encode('utf-8'))
    result = tree.find('./result')
    assert result is not None
    
    titles_in_li = [li.xpath('string(i)') for li in result.findall('.//li')]
    assert titles_in_li == [
        "Everyday Italian",
        "Harry Potter",
        "Learning XML",
    ]

def test_html_fragment_query_results_in_result_element():
    """Top-level XQuery with constructed HTML returns inside a <result> tag without escaping."""
    xml_books = """<?xml version="1.0"?>
<BOOKS>
  <ITEM>
    <TITLE>Learning XML</TITLE>
    <AUTHOR>Erik T. Ray</AUTHOR>
  </ITEM>
  <ITEM>
    <TITLE>Everyday Italian</TITLE>
    <AUTHOR>Giada De Laurentiis</AUTHOR>
  </ITEM>
</BOOKS>"""
    query = """
    xquery version "1.0";
    <h1>A list of books</h1>
    <p>Here are some interesting books:</p>
    <ul>{
      for $b in //BOOKS/ITEM
      order by $b/TITLE
      return <li><i>{ string($b/TITLE) }</i> by { string($b/AUTHOR) }</li>
    }</ul>
    """
    success, message, result_xml = XMLUtilities.execute_xquery(xml_books, query)
    assert success, message
    
    doc = etree.fromstring(result_xml.encode('utf-8'))
    result = doc.find('./result')
    assert result is not None, "Expected a <result> element wrapping output"
    
    h1 = result.find('h1')
    assert h1 is not None and h1.text == "A list of books"
    
    lis = result.findall('.//ul/li')
    assert len(lis) == 2
    assert [li.xpath('string(i)') for li in lis] == ["Everyday Italian", "Learning XML"]

if __name__ == "__main__":
    test_production_xquery()
    test_scalar_result_wrapped_in_xml()
    print("\n✓ All production tests passed!")
