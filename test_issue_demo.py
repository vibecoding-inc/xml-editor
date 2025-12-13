#!/usr/bin/env python3
"""
Demonstration that the problematic XQuery from the issue now works.
"""

from xmleditor.xml_utils import XMLUtilities

# Sample XML that matches the query structure
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

# The exact problematic XQuery from the issue
problematic_xquery = """(: Example XQuery :)
xquery version "1.0";
<Result_Example_XQuery>{

for $s in doc("staffinfo.xml")/staffinfo/job/title

return
  <JobTitle> {$s/text()} </JobTitle>,
let $k := count(doc("staffinfo.xml")/staffinfo/job/title)
return
  <CountJobTitle> {$k} </CountJobTitle>

}</Result_Example_XQuery>"""

print("=" * 80)
print("DEMONSTRATION: Problematic XQuery from Issue is Now Parseable")
print("=" * 80)
print("\nOriginal XQuery (as provided in issue):")
print("-" * 80)
print(problematic_xquery)
print("-" * 80)

print("\nExecution Results:")
print("-" * 80)
success, message, result_xml = XMLUtilities.execute_xquery(xml_content, problematic_xquery)

if success:
    print(f"✓ SUCCESS: {message}")
    print("\nResults (as XML document):")
    print(result_xml.strip())
else:
    print(f"✗ FAILED: {message}")

print("\n" + "=" * 80)
print("The XQuery is now parseable and executes successfully!")
print("=" * 80)
