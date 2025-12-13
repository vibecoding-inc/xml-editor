import re
from xmleditor.xml_utils import XMLUtilities


def test_template_dispersed_expressions():
    xml = """
    <root>
      <a id="42">Hello</a>
      <b><c>World</c></b>
    </root>
    """.strip()

    xq = (
        'declare namespace ex = "urn:ex";\n'
        '<Result data-id="{/root/a/@id}" note="pre{string-length(/root/a/text())}post">\n'
        '  Text: { /root/a/text() }\n'
        '  Nodes: { /root/b/c }\n'
        '  CountTitles: { count(/root//c) }\n'
        '  Escaped: {{ and }}\n'
        '</Result>'
    )

    ok, msg, out = XMLUtilities.execute_xquery(xml, xq)
    assert ok, msg
    assert len(out) == 1
    s = out[0]
    # Attribute AVT
    assert 'data-id="42"' in s
    assert 'note="pre5post"' in s
    # Text and node serialization
    assert 'Text: Hello' in s
    assert '<c>World</c>' in s
    # Escaped braces
    assert 'Escaped: { and }' in s
    # Count appears and is > 0
    m = re.search(r'CountTitles:\s*(\d+)', s)
    assert m, f"CountTitles not found in output: {s}"
    assert int(m.group(1)) > 0


def test_escaped_braces_literal_only():
    xml = '<doc/>'
    xq = 'Result: {{foo}} and {{bar}}'
    ok, msg, out = XMLUtilities.execute_xquery(xml, xq)
    assert ok, msg
    assert out == ['Result: {foo} and {bar}']


def test_sequence_rendering_in_text_and_attribute():
    xml = '<doc/>'
    xq = '<Seq val="{(1,2,3)}">{(1,2,3)}</Seq>'
    ok, msg, out = XMLUtilities.execute_xquery(xml, xq)
    assert ok, msg
    s = out[0]
    # Attribute becomes concatenated string
    assert 'val="123"' in s
    # Text content concatenated
    assert '>123<' in s


def test_namespace_usage_in_expression():
    xml = (
        '<ex:root xmlns:ex="urn:ex">\n'
        '  <ex:item>X</ex:item>\n'
        '</ex:root>'
    )
    xq = (
        'declare namespace ex = "urn:ex";\n'
        '<Out>{ /ex:root/ex:item/text() }</Out>'
    )
    ok, msg, out = XMLUtilities.execute_xquery(xml, xq)
    assert ok, msg
    assert out == ['<Out>X</Out>']
