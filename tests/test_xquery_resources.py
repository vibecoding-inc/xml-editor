#!/usr/bin/env python3
"""
Tests for external resource resolution in XQuery: doc(), wrapper attributes,
nested templates, and multiple FLWOR clauses.
"""

import os
from xmleditor.xml_utils import XMLUtilities


def _samples_dir():
    # Find samples directory from tests/ upward
    here = os.path.dirname(__file__)
    for _ in range(4):
        cand = os.path.abspath(os.path.join(here, 'samples'))
        if os.path.isdir(cand):
            return cand
        here = os.path.abspath(os.path.join(here, os.pardir))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'samples'))


def load_sample(path):
    sd = _samples_dir()
    with open(os.path.join(sd, path), 'r', encoding='utf-8') as f:
        return f.read()


def test_doc_function_staffinfo_titles():
    xml = load_sample('staffinfo.xml')
    # Query titles via doc() referencing the sample by basename
    query = 'for $s in doc("staffinfo.xml")/staffinfo/job/title return $s/text()'
    ok, msg, results = XMLUtilities.execute_xquery(xml, query, working_dir=_samples_dir())
    assert ok, msg
    # Ensure we got many titles and the first is President (sample ordering)
    assert len(results) >= 1
    assert 'President' in results[0]


def test_wrapper_attributes_preserved():
    xml = '<root><a>1</a><a>2</a></root>'
    query = '<Result id="x" class="c">{ for $n in //a return $n/text() }</Result>'
    ok, msg, results = XMLUtilities.execute_xquery(xml, query)
    assert ok, msg
    assert len(results) == 1
    out = results[0]
    assert out.startswith('<Result id="x" class="c">')
    assert out.endswith('</Result>')


def test_template_nested_element_constructors():
    xml = '<root><item>ok</item></root>'
    query = '{ <Wrap>{ //item/text() }</Wrap> }'
    ok, msg, results = XMLUtilities.execute_xquery(xml, query)
    assert ok, msg
    assert len(results) == 1
    assert '<Wrap>ok</Wrap>' in results[0]


def test_consecutive_for_clauses_in_template():
    xml = '<staffinfo><job><title>Alpha</title></job><job><title>Beta</title></job></staffinfo>'
    query = '{\nfor $s in //job/title\nreturn {$s/text()},\nfor $k in (1,2) return {$k}\n}'
    ok, msg, results = XMLUtilities.execute_xquery(xml, query)
    assert ok, msg
    out = results[0]
    # Contains both titles and numbers 1 and 2
    assert 'Alpha' in out and 'Beta' in out and '1' in out and '2' in out
