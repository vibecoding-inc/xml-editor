#!/usr/bin/env python3
"""
Test script for XQuery preprocessing functionality.
Tests the ability to handle complex XQuery syntax and convert it to XPath 3.0.
"""

from xmleditor.xml_utils import XMLUtilities

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

def test_xquery_preprocessing():
    """Test various XQuery preprocessing scenarios."""
    
    test_cases = [
        (
            "Original problematic query from issue",
            """(: Example XQuery :)
xquery version "1.0";
<Result_Example_XQuery>{

for $s in doc("staffinfo.xml")/staffinfo/job/title

return
  <JobTitle> {$s/text()} </JobTitle>,
let $k := count(doc("staffinfo.xml")/staffinfo/job/title)
return
  <CountJobTitle> {$k} </CountJobTitle>

}</Result_Example_XQuery>""",
            1,  # Expected: single XML wrapper containing titles and count
            True,
        ),
        (
            "XQuery with version declaration only",
            """xquery version "1.0";
//staffinfo/job/title/text()""",
            3,
            False,
        ),
        (
            "XQuery with comments",
            """(: This is a comment :)
//staffinfo/job/title/text()""",
            3,
            False,
        ),
        (
            "XQuery with doc() function",
            """doc("staffinfo.xml")/staffinfo/job/title/text()""",
            3,
            False,
        ),
        (
            "Simple XPath (should pass through)",
            """//staffinfo/job/title/text()""",
            3,
            False,
        ),
        (
            "Count query",
            """count(//staffinfo/job/title)""",
            1,
            False,
        ),
    ]
    
    print("Testing XQuery Preprocessing")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for description, query, expected_count, expect_wrapper in test_cases:
        print(f"\n{description}")
        print("-" * 80)
        print(f"Query: {query[:100]}..." if len(query) > 100 else f"Query: {query}")
        
        success, message, results = XMLUtilities.execute_xquery(xml_content, query)
        
        if success:
            actual_count = len(results)
            if actual_count == expected_count:
                print(f"✓ PASS: {message}")
                print(f"  Expected {expected_count} result(s), got {actual_count}")
                passed += 1
            else:
                print(f"✗ FAIL: Result count mismatch")
                print(f"  Expected {expected_count} result(s), got {actual_count}")
                failed += 1
            
            # Show first few results
            for i, result in enumerate(results[:3], 1):
                result_str = result.strip() if isinstance(result, str) else str(result)
                if len(result_str) > 50:
                    result_str = result_str[:50] + "..."
                print(f"    Result {i}: {result_str}")
            if len(results) > 3:
                print(f"    ... and {len(results) - 3} more")
            
            if expect_wrapper:
                assert actual_count == 1, "Wrapper query should return a single XML string"
                wrapped = results[0]
                assert "<Result_Example_XQuery>" in wrapped, "Wrapper element should be preserved"
                assert "<JobTitle>" in wrapped, "JobTitle elements should be rendered"
                assert "<CountJobTitle>" in wrapped, "Count element should be rendered"
        else:
            print(f"✗ FAIL: {message}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0

def test_preprocessing_function():
    """Test the preprocessing function directly."""
    
    print("\n\nTesting Preprocessing Function Directly")
    print("=" * 80)
    
    test_cases = [
        (
            "Remove comments",
            "(: comment :) //title",
            "//title"
        ),
        (
            "Remove version declaration",
            "xquery version \"1.0\"; //title",
            "//title"
        ),
        (
            "Remove doc() function",
            "doc(\"file.xml\")/path/to/element",
            "/path/to/element"
        ),
    ]
    
    for description, input_query, expected_pattern in test_cases:
        print(f"\n{description}")
        print(f"  Input:    {input_query}")
        result = XMLUtilities.preprocess_xquery(input_query)
        print(f"  Output:   {result}")
        print(f"  Expected: {expected_pattern}")
        
        if expected_pattern in result or result.strip() == expected_pattern.strip():
            print("  ✓ PASS")
        else:
            print("  ✗ FAIL")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    success = test_xquery_preprocessing()
    test_preprocessing_function()
    
    if success:
        print("\n✓ All tests passed!")
        exit(0)
    else:
        print("\n✗ Some tests failed!")
        exit(1)
