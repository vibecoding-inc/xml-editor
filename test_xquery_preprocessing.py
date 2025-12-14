#!/usr/bin/env python3
"""
Test script for XQuery fragment containers.
Verifies that multiple XQuery fragments embedded inside an XML file are
executed and aggregated into a single XML result document.
"""

from xmleditor.xml_utils import XMLUtilities
from lxml import etree

# Test XML content
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<staffinfo>
    <job>
        <title>Software Engineer</title>
    </job>
    <job>
        <title>Data Analyst</title>
    </job>
    <job>
        <title>Product Manager</title>
    </job>
</staffinfo>"""

def test_xquery_fragment_container():
    """Execute multiple XQuery fragments embedded in an XML document."""
    fragment_container = """<queries>
    <xquery>//staffinfo/job/title</xquery>
    <xquery>count(//staffinfo/job/title)</xquery>
</queries>"""
    
    success, message, result_xml = XMLUtilities.execute_xquery(xml_content, fragment_container)
    assert success, message
    
    wrapper = etree.fromstring(f"<root>{result_xml}</root>".encode('utf-8'))
    titles = wrapper.findall('.//title')
    assert [t.text for t in titles] == ["Software Engineer", "Data Analyst", "Product Manager"]
    count_text = wrapper.xpath('string(/root)')
    assert "3" in count_text
   
    print(message)

if __name__ == "__main__":
    test_xquery_fragment_container()
    print("\n✓ All tests passed!")
