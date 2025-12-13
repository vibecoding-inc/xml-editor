#!/usr/bin/env python3
"""
Demonstration that the problematic XQuery from the issue now works.
"""

import os
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

def _samples_dir():
    here = os.path.dirname(__file__)
    for _ in range(4):
        cand = os.path.abspath(os.path.join(here, 'samples'))
        if os.path.isdir(cand):
            return cand
        here = os.path.abspath(os.path.join(here, os.pardir))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'samples'))


def test_issue_demo_runs():
    samples_dir = _samples_dir()
    success, message, results = XMLUtilities.execute_xquery(xml_content, problematic_xquery, working_dir=samples_dir)
    assert success, message
    assert len(results) == 1
    wrapped = results[0]
    assert "<Result_Example_XQuery>" in wrapped
    assert "<JobTitle>" in wrapped
    assert "<CountJobTitle>" in wrapped
