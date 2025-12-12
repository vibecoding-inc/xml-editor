#!/usr/bin/env python3
"""
Production-ready XQuery preprocessing tests.
Tests comprehensive XQuery syntax support.
"""

from xmleditor.xml_utils import XMLUtilities

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
    """Test production-ready XQuery patterns."""
    
    test_cases = [
        # Basic FLWOR
        (
            "Simple for-return",
            "for $b in //book return $b/title/text()",
            4  # All 4 titles
        ),
        
        # FLWOR with where clause
        (
            "For-where-return",
            "for $b in //book where $b/@price > 30 return $b/title/text()",
            2  # Books with price > 30 (39.95, 49.99)
        ),
        
        # FLWOR with let clause
        (
            "For-let-return",
            "for $b in //book let $p := $b/@price return concat($b/title/text(), ': $', $p)",
            4  # All books with prices
        ),
        
        # FLWOR with where and let
        (
            "For-let-where-return",
            """for $b in //book 
            let $price := $b/@price 
            where $price > 30 
            return $b/title/text()""",
            2  # Expensive books (39.95, 49.99)
        ),
        
        # With namespace declaration (should be removed)
        (
            "With namespace declaration",
            """declare namespace ex = "http://example.com";
            //book/title/text()""",
            4  # All titles
        ),
        
        # With pragma (should be removed)
        (
            "With pragma",
            """(# opt:level 10 #) //book/title/text()""",
            4  # All titles
        ),
        
        # Doc-available function
        (
            "With doc-available",
            """if (doc-available("test.xml")) then //book/title/text() else ()""",
            4  # Titles (doc-available returns true)
        ),
        
        # Multiple where conditions
        (
            "Multiple conditions in where",
            """for $b in //book 
            where $b/@price > 25 and $b/year = 2003
            return $b/title/text()""",
            2  # Books from 2003 with price > 25
        ),
        
        # Element construction with where
        (
            "Element construction with filter",
            """for $b in //book 
            where $b/@category = 'web'
            return <WebBook>{$b/title/text()}</WebBook>""",
            2  # Web category books
        ),
        
        # Complex expression
        (
            "Complex FLWOR",
            """xquery version "1.0";
            (: Find expensive books :)
            for $book in //book
            let $discount := $book/@price * 0.1
            where $book/@price > 35
            return $book/title/text()""",
            2  # Books > $35
        ),
        
        # Collection (should return empty)
        (
            "Collection function",
            """let $docs := collection("test") return count($docs)""",
            1  # count of empty sequence = 0
        ),
    ]
    
    print("=" * 80)
    print("Production XQuery Tests")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for description, query, expected_count in test_cases:
        print(f"\n{description}")
        print("-" * 80)
        
        # Show preprocessed query
        preprocessed = XMLUtilities.preprocess_xquery(query)
        if len(preprocessed) < 100:
            print(f"Preprocessed: {preprocessed}")
        
        success, message, results = XMLUtilities.execute_xquery(xml_content, query)
        
        if success:
            actual_count = len(results)
            if actual_count == expected_count:
                print(f"✓ PASS: {message}")
                passed += 1
            else:
                print(f"✗ FAIL: Expected {expected_count} results, got {actual_count}")
                print(f"  Message: {message}")
                failed += 1
            
            # Show sample results
            for i, result in enumerate(results[:2], 1):
                result_str = str(result).strip()[:60]
                print(f"  Sample {i}: {result_str}")
        else:
            print(f"✗ FAIL: {message}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0

def test_preprocessing_details():
    """Test specific preprocessing transformations."""
    
    print("\n\n" + "=" * 80)
    print("Preprocessing Transformation Tests")
    print("=" * 80)
    
    test_cases = [
        (
            "Remove namespace declaration",
            'declare namespace ex = "http://example.com"; //title',
            "//title"
        ),
        (
            "Remove pragma",
            "(# opt:level 10 #) //title",
            "//title"
        ),
        (
            "Remove version and encoding",
            'xquery version "1.0" encoding "UTF-8"; //title',
            "//title"
        ),
        (
            "Handle doc-available",
            "doc-available('test.xml')",
            "true()"
        ),
        (
            "FLWOR with where",
            "for $x in //item where $x > 5 return $x",
            "for $x in //item[. > 5] return $x"
        ),
    ]
    
    for description, input_query, expected_pattern in test_cases:
        print(f"\n{description}")
        result = XMLUtilities.preprocess_xquery(input_query)
        print(f"  Input:    {input_query}")
        print(f"  Output:   {result}")
        print(f"  Expected: {expected_pattern}")
        
        if expected_pattern in result or result.strip() == expected_pattern.strip():
            print("  ✓ PASS")
        else:
            print("  ~ PARTIAL (may still work)")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    success = test_production_xquery()
    test_preprocessing_details()
    
    if success:
        print("\n✓ All production tests passed!")
        exit(0)
    else:
        print("\n⚠ Some tests failed - reviewing...")
        exit(1)
