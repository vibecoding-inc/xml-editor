"""
XQuery execution engine with template-first rendering.

Responsibilities:
- Detect and render XQuery direct element constructors with enclosed expressions
  across the entire template (including attributes).
- Evaluate each enclosed expression independently against the current document
  using elementpath's XPath 3.0 engine.
- Carry namespace declarations from the prolog into the expression context.
- Resolve doc() calls without sandboxing (as per project requirements).

This module intentionally avoids wrapper reconstruction. The output is exactly
the interleaving of literal segments with evaluated expression results.
"""
from __future__ import annotations

from typing import List, Tuple, Dict
import re
import os
from lxml import etree

try:
    from elementpath.xpath30 import XPath30Parser
    import elementpath
    XQUERY_AVAILABLE = True
except Exception:
    XQUERY_AVAILABLE = False


def _strip_comments_and_version(text: str) -> str:
    """Remove XQuery comments, pragmas and version decl but keep other declares."""
    stripped = re.sub(r"\(:.*?:\)", "", text, flags=re.DOTALL)
    stripped = re.sub(r"\(#.*?#\)", "", stripped, flags=re.DOTALL)
    stripped = re.sub(r'xquery\s+version\s+"[^"]*"(?:\s+encoding\s+"[^"]*")?\s*;\s*', '', stripped, flags=re.IGNORECASE)
    return stripped


def _parse_prolog_namespaces(text: str) -> Tuple[Dict[str, str], str]:
    """Extract declare namespace prolog entries and return mapping and the body without them."""
    ns_map: Dict[str, str] = {}

    def repl(m: re.Match) -> str:
        prefix = m.group('prefix')
        uri = m.group('uri')
        ns_map[prefix] = uri
        return ''

    body = re.sub(r'(?im)^\s*declare\s+namespace\s+(?P<prefix>\w+)\s*=\s*"(?P<uri>[^"]*)"\s*;\s*', repl, text)
    return ns_map, body


def _tokenize_template(template: str) -> List[Tuple[str, str]]:
    """Tokenize into [('lit', text)|('expr', code)] with nested braces and escaped {{ }} in literal regions."""
    tokens: List[Tuple[str, str]] = []
    i = 0
    n = len(template)
    buf: List[str] = []
    depth = 0

    def flush_literal():
        nonlocal buf
        if buf:
            tokens.append(('lit', ''.join(buf)))
            buf = []

    expr_buf: List[str] = []

    while i < n:
        ch = template[i]
        if depth == 0:
            if ch == '{':
                # Escaped literal brace {{ -> {
                if i + 1 < n and template[i + 1] == '{':
                    buf.append('{')
                    i += 2
                    continue
                # start expression
                flush_literal()
                depth = 1
                expr_buf = []
                i += 1
                continue
            elif ch == '}':
                # Escaped literal brace }} -> }
                if i + 1 < n and template[i + 1] == '}':
                    buf.append('}')
                    i += 2
                    continue
                # stray closing brace in literal region, treat literally
                buf.append('}')
                i += 1
                continue
            else:
                buf.append(ch)
                i += 1
                continue
        else:
            # inside expression region
            if ch == '{':
                depth += 1
                expr_buf.append(ch)
                i += 1
                continue
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    code = ''.join(expr_buf).strip()
                    tokens.append(('expr', code))
                    expr_buf = []
                    i += 1
                    continue
                else:
                    expr_buf.append('}')
                    i += 1
                    continue
            else:
                expr_buf.append(ch)
                i += 1
                continue

    if depth != 0:
        raise ValueError('unmatched braces in template')

    flush_literal()
    return tokens


def _to_concat_literal(text: str) -> str:
    """Build a concat() expression from a literal containing {expr} placeholders."""
    parts: List[str] = []
    buf: List[str] = []
    depth = 0
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == '{':
            if depth == 0 and buf:
                lit = ''.join(buf)
                parts.append('"' + lit.replace('"', '""') + '"')
                buf = []
            depth += 1
            i += 1
            continue
        if ch == '}':
            depth -= 1
            if depth == 0:
                expr = ''.join(buf).strip()
                if expr:
                    parts.append(expr)
                buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    if buf:
        lit = ''.join(buf)
        parts.append('"' + lit.replace('"', '""') + '"')
    if not parts:
        return '""'
    if len(parts) == 1:
        return parts[0]
    return 'concat(' + ', '.join(parts) + ')'


def _convert_element_constructors_generic(expr: str) -> str:
    """Convert element constructors to concat expressions preserving {expr} interpolation."""
    element_pattern = re.compile(r'<(?P<tag>[\w:-]+)(?P<attrs>[^>]*)>(?P<body>.*?)</(?P=tag)>', re.DOTALL)

    def repl(match: re.Match) -> str:
        raw = match.group(0)
        return _to_concat_literal(raw)

    return element_pattern.sub(repl, expr)


def _resolve_external_resources(expr: str, working_dir: str | None = None) -> Tuple[str, Dict[str, etree._Element]]:
    """
    Resolve external resources for expressions:
    - doc("path") is rewritten to root($__doc_N) and the parsed document is bound
      into the variables mapping.
    - If a referenced document cannot be resolved, raise an error to surface it
      to the caller instead of silently returning an empty sequence.

    Search order for doc paths (if relative):
    1) Current working directory (CWD)
    2) Project root (directory above xmleditor)
    3) CWD/samples
    4) Project root/samples
    Absolute paths are used as-is.
    """
    variables: Dict[str, etree._Element] = {}
    idx = 0

    def repl(m: re.Match) -> str:
        nonlocal idx
        path = m.group(2).strip()
        # Build candidate locations
        candidates = []
        if os.path.isabs(path):
            candidates.append(path)
        else:
            cwd = working_dir or os.getcwd()
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            # Directly under provided working dir (if any), CWD and project root
            candidates.append(os.path.abspath(os.path.join(cwd, path)))
            candidates.append(os.path.abspath(os.path.join(project_root, path)))
        try:
            last_err = None
            parsed_doc = None
            for candidate in candidates:
                try:
                    # Parse as ElementTree to behave like a document node
                    parsed_doc = etree.parse(candidate)
                    break
                except Exception as e:
                    last_err = e
                    parsed_doc = None
            if parsed_doc is None:
                # Surface a clear error to the UI/tests
                location_hint = path if os.path.isabs(path) else f"{path} (searched: {', '.join(candidates)})"
                raise FileNotFoundError(f"doc() could not resolve '{location_hint}'")
            var_name = f'__doc_{idx}'
            variables[var_name] = parsed_doc
            idx += 1
            # Bind ElementTree to a variable; elementpath supports tree nodes.
            # Use the variable directly in path expressions: $name/...
            return f'${var_name}'
        except Exception as e:
            # Reraise to be handled by the caller (we don't silently ignore doc failures)
            raise e

    expr = re.sub(r'doc\(\s*([\"\'])\s*(.*?)\s*\1\s*\)', repl, expr)
    # collection() -> empty sequence for now
    expr = re.sub(r'collection\(\s*([\"\'])\s*.*?\s*\1\s*\)', '()', expr)
    return expr, variables


def _evaluate_expression(expr: str, tree: etree._Element, namespaces: Dict[str, str], working_dir: str | None = None) -> List[str]:
    parser = XPath30Parser()
    if namespaces:
        # Make prefixes available at parse-time
        parser.namespaces.update(namespaces)
    # Replace bare enclosed expressions { ... } (not in literals) with parentheses to
    # satisfy the XPath parser when authors write XQuery-style blocks inside expressions.
    def replace_bare_enclosed(s: str) -> str:
        out: List[str] = []
        i = 0
        n = len(s)
        depth = 0
        in_str = False
        str_ch = ''
        buf: List[str] = []
        while i < n:
            ch = s[i]
            if in_str:
                buf.append(ch)
                if ch == str_ch:
                    in_str = False
                i += 1
                continue
            if ch in ('"', "'"):
                buf.append(ch)
                in_str = True
                str_ch = ch
                i += 1
                continue
            if ch == '{':
                # start capturing until matching }
                if depth == 0:
                    # flush buf to out
                    if buf:
                        out.append(''.join(buf))
                        buf = []
                depth += 1
                # use '(' instead of '{' at top-level only
                buf.append('(' if depth == 1 else '{')
                i += 1
                continue
            if ch == '}':
                if depth > 0:
                    # close capture
                    buf.append(')' if depth == 1 else '}')
                    depth -= 1
                    i += 1
                    continue
            buf.append(ch)
            i += 1
        if buf:
            out.append(''.join(buf))
        return ''.join(out)

    # Normalize expression for element constructors first so {expr} inside
    # direct constructors is preserved as concat arguments.
    processed = _convert_element_constructors_generic(expr)
    # Then make XQuery-style bare enclosed expressions acceptable to the XPath parser
    processed = replace_bare_enclosed(processed)
    processed, variables = _resolve_external_resources(processed, working_dir=working_dir)
    query = parser.parse(processed)
    context = elementpath.XPathContext(tree, namespaces=namespaces if namespaces else None,
                                       variables=variables if variables else None)
    result = query.evaluate(context=context)

    if result is None:
        items: List = []
    elif isinstance(result, (list, tuple)):
        items = list(result)
    elif hasattr(result, '__iter__') and not isinstance(result, str):
        items = list(result)
    else:
        items = [result]

    rendered: List[str] = []
    for item in items:
        if hasattr(item, 'elem'):
            rendered.append(etree.tostring(item.elem, encoding='unicode', pretty_print=True))
        elif isinstance(item, str):
            rendered.append(item)
        elif hasattr(item, 'value'):
            rendered.append(str(item.value))
        else:
            rendered.append(str(item))
    return rendered


def _render_template(xml_string: str, xquery_string: str, working_dir: str | None = None) -> Tuple[bool, str, List[str]]:
    # Keep comments/pragma/version out but preserve and capture namespaces
    cleaned = _strip_comments_and_version(xquery_string)
    namespaces, body = _parse_prolog_namespaces(cleaned)

    tree = etree.fromstring(xml_string.encode('utf-8'))
    tokens = _tokenize_template(body)

    out_parts: List[str] = []
    for kind, text in tokens:
        if kind == 'lit':
            out_parts.append(text)
        else:
            if text == '':
                out_parts.append('')
            else:
                out_parts.extend(_evaluate_expression(text, tree, namespaces, working_dir=working_dir))

    rendered = ''.join(out_parts).strip()
    return True, f"Query executed successfully (1 result(s))", [rendered]


def _has_balanced_braces(s: str) -> bool:
    depth = 0
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == '{':
            if i + 1 < n and s[i + 1] == '{':
                i += 2
                continue
            depth += 1
        elif ch == '}':
            if i + 1 < n and s[i + 1] == '}':
                i += 2
                continue
            depth -= 1
            if depth < 0:
                return False
        i += 1
    return depth == 0


def execute_xquery(xml_string: str, xquery_string: str, working_dir: str | None = None) -> Tuple[bool, str, List[str]]:
    """Public entry point used by XMLUtilities.execute_xquery."""
    if not XQUERY_AVAILABLE:
        return False, "XQuery support not available. Install 'elementpath' package.", []

    try:
        stripped = _strip_comments_and_version(xquery_string).strip()
        # Template-first: if braces are present and balanced, render template
        if ('{' in stripped and '}' in stripped and _has_balanced_braces(stripped)):
            return _render_template(xml_string, xquery_string, working_dir=working_dir)

        # No enclosed expressions: evaluate as a single XPath/XQuery expression
        tree = etree.fromstring(xml_string.encode('utf-8'))
        # Carry namespaces for bare expressions as well
        ns_map, body = _parse_prolog_namespaces(stripped)
        processed, variables = _resolve_external_resources(body, working_dir=working_dir)
        parser = XPath30Parser()
        if ns_map:
            parser.namespaces.update(ns_map)
        query = parser.parse(processed.strip())
        context = elementpath.XPathContext(tree, namespaces=ns_map if ns_map else None,
                                           variables=variables if variables else None)
        result = query.evaluate(context=context)

        if result is None:
            items: List = []
        elif isinstance(result, (list, tuple)):
            items = list(result)
        elif hasattr(result, '__iter__') and not isinstance(result, str):
            items = list(result)
        else:
            items = [result]

        formatted: List[str] = []
        for item in items:
            if hasattr(item, 'elem'):
                formatted.append(etree.tostring(item.elem, encoding='unicode', pretty_print=True))
            elif isinstance(item, str):
                formatted.append(item)
            elif hasattr(item, 'value'):
                formatted.append(str(item.value))
            else:
                formatted.append(str(item))

        return True, f"Query executed successfully ({len(formatted)} result(s))", formatted
    except Exception as e:
        return False, f"XQuery execution error: {str(e)}", []
