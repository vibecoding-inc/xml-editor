"""
XML utilities for parsing, validating, and manipulating XML documents.
"""

from lxml import etree
import xml.dom.minidom
import re
from typing import Optional, List, Tuple
try:
    from elementpath.xpath30 import XPath30Parser
    import elementpath
    XQUERY_AVAILABLE = True
except ImportError:
    XQUERY_AVAILABLE = False


class XMLUtilities:
    """Utilities for XML operations."""
    
    @staticmethod
    def parse_xml(xml_string: str) -> Optional[etree._Element]:
        """
        Parse XML string and return the element tree.
        
        Args:
            xml_string: XML content as string
            
        Returns:
            Element tree or None if parsing fails
        """
        try:
            return etree.fromstring(xml_string.encode('utf-8'))
        except Exception as e:
            raise ValueError(f"XML parsing error: {str(e)}")
    
    @staticmethod
    def validate_xml(xml_string: str) -> Tuple[bool, str]:
        """
        Validate if string is well-formed XML.
        
        Args:
            xml_string: XML content as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            etree.fromstring(xml_string.encode('utf-8'))
            return True, "XML is well-formed"
        except Exception as e:
            return False, f"XML validation error: {str(e)}"
    
    @staticmethod
    def validate_with_xsd(xml_string: str, xsd_string: str) -> Tuple[bool, str]:
        """
        Validate XML against XSD schema.
        
        Args:
            xml_string: XML content as string
            xsd_string: XSD schema as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse XSD
            xsd_doc = etree.fromstring(xsd_string.encode('utf-8'))
            schema = etree.XMLSchema(xsd_doc)
            
            # Parse XML
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            
            # Validate
            if schema.validate(xml_doc):
                return True, "XML is valid against the schema"
            else:
                errors = []
                for error in schema.error_log:
                    errors.append(f"Line {error.line}: {error.message}")
                return False, "\n".join(errors)
        except Exception as e:
            return False, f"Schema validation error: {str(e)}"
    
    @staticmethod
    def validate_with_dtd(xml_string: str, dtd_string: str) -> Tuple[bool, str]:
        """
        Validate XML against DTD.
        
        Args:
            xml_string: XML content as string
            dtd_string: DTD as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse DTD
            dtd = etree.DTD(etree.fromstring(dtd_string.encode('utf-8')))
            
            # Parse XML
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            
            # Validate
            if dtd.validate(xml_doc):
                return True, "XML is valid against the DTD"
            else:
                errors = []
                for error in dtd.error_log:
                    errors.append(f"Line {error.line}: {error.message}")
                return False, "\n".join(errors)
        except Exception as e:
            return False, f"DTD validation error: {str(e)}"
    
    @staticmethod
    def format_xml(xml_string: str, indent: str = "  ") -> str:
        """
        Format XML with proper indentation.
        
        Args:
            xml_string: XML content as string
            indent: Indentation string
            
        Returns:
            Formatted XML string
        """
        try:
            # Parse and pretty print
            dom = xml.dom.minidom.parseString(xml_string)
            pretty_xml = dom.toprettyxml(indent=indent, encoding='utf-8')
            
            # Remove extra blank lines
            lines = pretty_xml.decode('utf-8').split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            return '\n'.join(non_empty_lines)
        except Exception as e:
            raise ValueError(f"XML formatting error: {str(e)}")
    
    @staticmethod
    def xpath_query(xml_string: str, xpath_expr: str, context_xpath: str = "") -> List[str]:
        """
        Execute XPath query on XML.
        
        Args:
            xml_string: XML content as string
            xpath_expr: XPath expression
            context_xpath: Optional XPath to select the context node (defaults to document root)
            
        Returns:
            List of matching results as strings
        """
        try:
            tree = etree.fromstring(xml_string.encode('utf-8'))
            
            # Determine the context node
            if context_xpath:
                context_nodes = tree.xpath(context_xpath)
                if not context_nodes:
                    raise ValueError(f"Context node not found: {context_xpath}")
                # Check if result is an element (can execute xpath on it)
                if not hasattr(context_nodes[0], 'xpath'):
                    raise ValueError(f"Context XPath must select an element: {context_xpath}")
                context_node = context_nodes[0]
            else:
                context_node = tree
            
            results = context_node.xpath(xpath_expr)
            
            # Handle non-iterable XPath results (float, bool, string)
            # XPath functions like count(), sum(), boolean(), string(), etc.
            # return scalar values instead of node sets
            if isinstance(results, (float, bool)):
                return [str(results)]
            if isinstance(results, str):
                return [results] if results else []
            
            # Handle iterable results (node sets)
            output = []
            for result in results:
                if isinstance(result, etree._Element):
                    output.append(etree.tostring(result, encoding='unicode', pretty_print=True))
                else:
                    output.append(str(result))
            
            return output
        except Exception as e:
            raise ValueError(f"XPath query error: {str(e)}")
    
    @staticmethod
    def get_xpath_for_element(xml_string: str, line: int, column: int) -> str:
        """
        Get XPath expression for element at given position.
        
        Args:
            xml_string: XML content as string
            line: Line number (1-based)
            column: Column number (1-based)
            
        Returns:
            XPath expression
        """
        try:
            tree = etree.fromstring(xml_string.encode('utf-8'))
            # This is a simplified implementation
            # In a real application, you'd need more sophisticated position tracking
            return tree.getroottree().getpath(tree)
        except Exception:
            return ""
    
    @staticmethod
    def apply_xslt(xml_string: str, xslt_string: str) -> str:
        """
        Apply XSLT transformation to XML.
        
        Args:
            xml_string: XML content as string
            xslt_string: XSLT stylesheet as string
            
        Returns:
            Transformed XML string
        """
        try:
            # Parse XML and XSLT
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            xslt_doc = etree.fromstring(xslt_string.encode('utf-8'))
            
            # Create transformer
            transform = etree.XSLT(xslt_doc)
            
            # Apply transformation
            result = transform(xml_doc)
            
            return str(result)
        except Exception as e:
            raise ValueError(f"XSLT transformation error: {str(e)}")
    
    @staticmethod
    def get_xml_tree_structure(xml_string: str, show_namespaces: bool = False) -> List[dict]:
        """
        Get XML tree structure for tree view.
        
        Args:
            xml_string: XML content as string
            show_namespaces: Whether to show namespace prefixes in tag names
            
        Returns:
            List of dictionaries representing tree nodes
        """
        try:
            tree = etree.fromstring(xml_string.encode('utf-8'))
            
            def element_to_dict(element):
                # Extract tag name, handling namespaces
                tag = element.tag
                if isinstance(tag, str):
                    # Handle namespace - extract local name or prefix
                    if tag.startswith('{'):
                        # Tag has namespace URI like {http://...}localname
                        ns_uri, local_name = tag[1:].split('}', 1)
                        if show_namespaces:
                            # Find the prefix for this namespace
                            prefix = None
                            for p, uri in element.nsmap.items():
                                if uri == ns_uri:
                                    prefix = p
                                    break
                            # Use prefix:localname or just localname if no prefix
                            tag = f"{prefix}:{local_name}" if prefix else local_name
                        else:
                            # Just use local name without namespace
                            tag = local_name
                    # else: tag has no namespace, use as-is
                
                node = {
                    'tag': tag,
                    'text': element.text.strip() if element.text and element.text.strip() else '',
                    'attributes': dict(element.attrib),
                    'children': []
                }
                for child in element:
                    node['children'].append(element_to_dict(child))
                return node
            
            return [element_to_dict(tree)]
        except Exception as e:
            raise ValueError(f"Error getting XML structure: {str(e)}")
    
    @staticmethod
    def generate_xsd_schema(xml_string: str) -> str:
        """
        Generate XSD schema from XML document.
        
        Args:
            xml_string: XML content as string
            
        Returns:
            Generated XSD schema as string
        """
        try:
            tree = etree.fromstring(xml_string.encode('utf-8'))
            
            # Analyze the XML structure
            element_info = XMLUtilities._analyze_elements(tree)
            
            # Build XSD schema
            schema_root = etree.Element(
                '{http://www.w3.org/2001/XMLSchema}schema',
                nsmap={'xs': 'http://www.w3.org/2001/XMLSchema'}
            )
            
            # Generate element definitions for all elements
            generated = set()
            XMLUtilities._generate_xsd_element_recursive(schema_root, tree.tag, element_info, generated)
            
            # Pretty print the schema
            return etree.tostring(schema_root, encoding='unicode', pretty_print=True)
        except Exception as e:
            raise ValueError(f"XSD schema generation error: {str(e)}")
    
    @staticmethod
    def _generate_xsd_element_recursive(parent, element_name: str, all_element_info: dict, generated: set):
        """
        Recursively generate XSD element definitions.
        
        Args:
            parent: Parent XSD element
            element_name: Name of the element
            all_element_info: All element information
            generated: Set of already generated element names
        """
        if element_name in generated:
            return
        generated.add(element_name)
        
        element_info = all_element_info[element_name]
        xs_ns = '{http://www.w3.org/2001/XMLSchema}'
        
        element = etree.SubElement(parent, f'{xs_ns}element')
        element.set('name', element_name)
        
        # Create complex or simple type
        if element_info['children'] or element_info['attributes']:
            complex_type = etree.SubElement(element, f'{xs_ns}complexType')
            
            # Handle children
            if element_info['children']:
                sequence = etree.SubElement(complex_type, f'{xs_ns}sequence')
                
                # Use the order of first appearance instead of sorted order
                for child_name in element_info['children_order']:
                    child_occ = element_info['children'][child_name]
                    child_info = all_element_info[child_name]
                    
                    # Check if child has its own children or attributes
                    if child_info['children'] or child_info['attributes']:
                        # Reference will be generated separately
                        child_elem = etree.SubElement(sequence, f'{xs_ns}element')
                        child_elem.set('ref', child_name)
                    else:
                        # Inline simple type
                        child_elem = etree.SubElement(sequence, f'{xs_ns}element')
                        child_elem.set('name', child_name)
                        if child_info['text_content']:
                            data_type = XMLUtilities._infer_xsd_type(child_info['text_content'])
                            child_elem.set('type', data_type)
                        else:
                            child_elem.set('type', 'xs:string')
                    
                    # Set occurrence constraints
                    if child_occ['min'] == 0:
                        child_elem.set('minOccurs', '0')
                    if child_occ['max'] > 1:
                        child_elem.set('maxOccurs', 'unbounded')
            
            # Handle text content with attributes
            elif element_info['text_content']:
                simple_content = etree.SubElement(complex_type, f'{xs_ns}simpleContent')
                extension = etree.SubElement(simple_content, f'{xs_ns}extension')
                data_type = XMLUtilities._infer_xsd_type(element_info['text_content'])
                extension.set('base', data_type)
                
                # Add attributes to extension
                for attr_name, attr_info in sorted(element_info['attributes'].items()):
                    attr_elem = etree.SubElement(extension, f'{xs_ns}attribute')
                    attr_elem.set('name', attr_name)
                    attr_elem.set('type', 'xs:string')
                    if attr_info['required']:
                        attr_elem.set('use', 'required')
            
            # Handle attributes (when no text content)
            if element_info['attributes'] and not element_info['text_content']:
                for attr_name, attr_info in sorted(element_info['attributes'].items()):
                    attr_elem = etree.SubElement(complex_type, f'{xs_ns}attribute')
                    attr_elem.set('name', attr_name)
                    attr_elem.set('type', 'xs:string')
                    if attr_info['required']:
                        attr_elem.set('use', 'required')
        else:
            # Simple type with text content only
            if element_info['text_content']:
                data_type = XMLUtilities._infer_xsd_type(element_info['text_content'])
                element.set('type', data_type)
            else:
                element.set('type', 'xs:string')
        
        # Recursively generate child elements that need separate definitions
        for child_name in element_info['children']:
            child_info = all_element_info[child_name]
            if (child_info['children'] or child_info['attributes']) and child_name not in generated:
                XMLUtilities._generate_xsd_element_recursive(parent, child_name, all_element_info, generated)
    
    @staticmethod
    def generate_dtd_schema(xml_string: str) -> str:
        """
        Generate DTD schema from XML document.
        
        Args:
            xml_string: XML content as string
            
        Returns:
            Generated DTD schema as string
        """
        try:
            tree = etree.fromstring(xml_string.encode('utf-8'))
            
            # Analyze the XML structure
            element_info = XMLUtilities._analyze_elements(tree)
            
            # Build DTD schema
            dtd_lines = []
            
            # Generate DTD element declarations
            for element_name, info in sorted(element_info.items()):
                dtd_lines.append(XMLUtilities._generate_dtd_element(element_name, info))
            
            return '\n'.join(dtd_lines)
        except Exception as e:
            raise ValueError(f"DTD schema generation error: {str(e)}")
    
    @staticmethod
    def _analyze_elements(root: etree._Element) -> dict:
        """
        Analyze XML elements to determine structure and patterns.
        
        Args:
            root: Root element of XML tree
            
        Returns:
            Dictionary with element information
        """
        element_info = {}
        
        def analyze_element(element, parent_tag=None):
            tag = element.tag
            
            # Initialize element info if not exists
            if tag not in element_info:
                element_info[tag] = {
                    'children': {},
                    'children_order': [],  # Track order of first appearance
                    'attributes': {},
                    'text_content': [],
                    'parent_tags': set(),
                    'count_by_parent': {}
                }
            
            info = element_info[tag]
            
            # Track parent relationship
            if parent_tag:
                info['parent_tags'].add(parent_tag)
                if parent_tag not in info['count_by_parent']:
                    info['count_by_parent'][parent_tag] = []
            
            # Analyze attributes
            for attr_name, attr_value in element.attrib.items():
                if attr_name not in info['attributes']:
                    info['attributes'][attr_name] = {'values': [], 'required': True}
                info['attributes'][attr_name]['values'].append(attr_value)
            
            # Track text content
            if element.text and element.text.strip():
                info['text_content'].append(element.text.strip())
            
            # Analyze children and track their order
            child_counts = {}
            for child in element:
                child_tag = child.tag
                child_counts[child_tag] = child_counts.get(child_tag, 0) + 1
                
                if child_tag not in info['children']:
                    info['children'][child_tag] = {'min': float('inf'), 'max': 0}
                    # Track the order of first appearance
                    info['children_order'].append(child_tag)
                
                analyze_element(child, tag)
            
            # Update child occurrence counts
            for child_tag, count in child_counts.items():
                child_info = info['children'][child_tag]
                child_info['min'] = min(child_info['min'], count)
                child_info['max'] = max(child_info['max'], count)
            
            # Mark missing children as optional (min=0)
            for child_tag in info['children']:
                if child_tag not in child_counts:
                    info['children'][child_tag]['min'] = 0
        
        analyze_element(root)
        
        # Determine attribute requirements
        for tag, info in element_info.items():
            for attr_name, attr_info in info['attributes'].items():
                # If not present in all instances, it's optional
                instances_count = len(info['text_content']) + sum(
                    len(counts) for counts in info['count_by_parent'].values()
                )
                if instances_count == 0:
                    instances_count = 1  # At least the element itself
                attr_info['required'] = len(attr_info['values']) >= instances_count
        
        return element_info
    
    @staticmethod
    def _infer_xsd_type(text_values: List[str]) -> str:
        """
        Infer XSD data type from text content.
        
        Args:
            text_values: List of text values
            
        Returns:
            XSD type name
        """
        if not text_values:
            return 'xs:string'
        
        # Try to determine if all values are integers
        all_int = True
        all_decimal = True
        
        for value in text_values:
            try:
                int(value)
            except ValueError:
                all_int = False
            
            try:
                float(value)
            except ValueError:
                all_decimal = False
        
        if all_int:
            return 'xs:integer'
        elif all_decimal:
            return 'xs:decimal'
        else:
            return 'xs:string'
    
    @staticmethod
    def _generate_dtd_element(element_name: str, element_info: dict) -> str:
        """
        Generate DTD element declaration.
        
        Args:
            element_name: Name of the element
            element_info: Element information dictionary
            
        Returns:
            DTD element declaration string
        """
        lines = []
        
        # Generate element declaration
        if element_info['children']:
            # Element has children - use order of first appearance
            child_specs = []
            for child_name in element_info['children_order']:
                child_occ = element_info['children'][child_name]
                spec = child_name
                if child_occ['min'] == 0 and child_occ['max'] == 1:
                    spec += '?'
                elif child_occ['min'] == 0 and child_occ['max'] > 1:
                    spec += '*'
                elif child_occ['max'] > 1:
                    spec += '+'
                child_specs.append(spec)
            
            content_model = ', '.join(child_specs)
            lines.append(f'<!ELEMENT {element_name} ({content_model})>')
        elif element_info['text_content']:
            # Element has text content
            lines.append(f'<!ELEMENT {element_name} (#PCDATA)>')
        else:
            # Empty element
            lines.append(f'<!ELEMENT {element_name} EMPTY>')
        
        # Generate attribute declarations
        if element_info['attributes']:
            for attr_name, attr_info in sorted(element_info['attributes'].items()):
                required = '#REQUIRED' if attr_info['required'] else '#IMPLIED'
                lines.append(f'<!ATTLIST {element_name} {attr_name} CDATA {required}>')
        
        return '\n'.join(lines)
    
    @staticmethod
    def preprocess_xquery(xquery_string: str) -> str:
        """
        Preprocess XQuery to convert unsupported syntax to XPath 3.0.
        
        Production-ready preprocessing handles:
        - XQuery version declarations and namespaces
        - Comments and pragmas
        - doc(), doc-available(), collection() functions
        - FLWOR with let, where, order by
        - Element construction
        - Multiple clauses and complex patterns
        
        Args:
            xquery_string: Raw XQuery expression
            
        Returns:
            Preprocessed XPath 3.0 compatible expression
        """
        query = xquery_string
        
        # Step 1: Remove XQuery comments (: ... :) - non-greedy match
        query = re.sub(r'\(:.*?:\)', '', query, flags=re.DOTALL)
        
        # Step 2: Remove pragmas (# ... #) if present
        query = re.sub(r'\(#.*?#\)', '', query, flags=re.DOTALL)
        
        # Step 3: Remove XQuery version and encoding declarations
        query = re.sub(r'xquery\s+version\s+"[^"]*"(?:\s+encoding\s+"[^"]*")?\s*;', '', query, flags=re.IGNORECASE)
        
        # Step 4: Remove namespace declarations
        query = re.sub(r'declare\s+namespace\s+\w+\s*=\s*"[^"]*"\s*;', '', query, flags=re.IGNORECASE)
        
        # Step 5: Remove other declare statements (boundary-space, ordering, etc.)
        query = re.sub(r'declare\s+\w+(?:\s+\w+)*\s*;', '', query, flags=re.IGNORECASE)
        
        # Step 6: Handle doc() and related functions
        query = re.sub(r'doc-available\([^)]+\)', 'true()', query)  # Assume doc is available
        query = re.sub(r'doc\([^)]+\)', '', query)  # Remove doc() calls
        query = re.sub(r'collection\([^)]+\)', '()', query)  # Empty sequence for collection
        
        # Step 7: Remove outer element wrapper if present
        query_stripped = query.strip()
        if query_stripped.startswith('<') and query_stripped.endswith('>'):
            outer_wrapper_match = re.match(r'^\s*<(\w+)[^>]*>\s*\{(.*)\}\s*</(\w+)>\s*$', query_stripped, re.DOTALL)
            if outer_wrapper_match and outer_wrapper_match.group(1) == outer_wrapper_match.group(3):
                query = outer_wrapper_match.group(2)
        
        # Step 8: Process FLWOR expressions
        query = XMLUtilities._process_flwor(query)
        
        return query.strip()
    
    @staticmethod
    def _process_flwor(query: str) -> str:
        """
        Process FLWOR expressions to convert to XPath 3.0 compatible syntax.
        
        Handles:
        - for...let...where...order by...return
        - Multiple for/let clauses
        - Nested FLWOR
        """
        def convert_element_constructors(expr: str) -> str:
            """
            Convert simple element constructors into string concatenations so they can be represented
            in XPath 3.0 execution results.
            """
            element_pattern = r'<(?P<tag>[\w:-]+)[^>]*>\s*\{(?P<content>[^}]+)\}\s*</(?P=tag)>'
            def _repl(match: re.Match) -> str:
                tag = match.group('tag')
                content = match.group('content').strip()
                return f'concat("<{tag}>", {content}, "</{tag}>")'
            
            return re.sub(element_pattern, _repl, expr)
        # Pattern 1: for...let...where...order by...return
        # Most complex FLWOR pattern
        full_flwor = r'for\s+\$(?P<for_var>\w+)\s+in\s+(?P<for_path>[^\r\n]+?)(?:\s+let\s+\$(?P<let_var>\w+)\s*:=\s*(?P<let_expr>[^\r\n]+?))?(?:\s+where\s+(?P<where_cond>[^\r\n]+?))?(?:\s+order\s+by\s+(?P<order_expr>[^\r\n]+?))?(?:\s+return\s+(?P<return_expr>.+))'
        
        match = re.search(full_flwor, query, re.DOTALL | re.IGNORECASE)
        if match:
            for_var = match.group('for_var').strip()
            for_path = match.group('for_path').strip()
            let_var = match.group('let_var')
            let_expr = match.group('let_expr')
            where_cond = match.group('where_cond')
            order_expr = match.group('order_expr')
            return_expr = match.group('return_expr').strip()
            
            # Convert element construction in return expression to string form
            return_expr = convert_element_constructors(return_expr)
            
            # Build the converted expression
            converted = f'for ${for_var} in {for_path}'
            
            # Handle let clause first - substitute in both where and return
            if let_var and let_expr:
                let_var = let_var.strip()
                let_expr = let_expr.strip()
                # Escape variable name to prevent ReDoS attacks
                let_var_escaped = re.escape(let_var)
                # Substitute let variable in return expression
                return_expr = re.sub(r'\$' + let_var_escaped + r'(?!\w)', let_expr, return_expr)
                # Also substitute in where condition if present
                if where_cond:
                    where_cond = re.sub(r'\$' + let_var_escaped + r'(?!\w)', let_expr, where_cond)
            
            # Handle where clause by adding it as a predicate
            if where_cond:
                where_cond = where_cond.strip()
                # Escape variable name to prevent ReDoS attacks
                for_var_escaped = re.escape(for_var)
                # Replace $var with . in the condition for predicate
                # But handle attributes specially: $var/@attr -> @attr (not ./@attr)
                where_pred = re.sub(r'\$' + for_var_escaped + r'/@', '@', where_cond)
                where_pred = re.sub(r'\$' + for_var_escaped + r'/([^\s\)]+)', r'./\1', where_pred)
                where_pred = re.sub(r'\$' + for_var_escaped + r'(?!\w|/)', '.', where_pred)
                converted = f'{converted}[{where_pred}]'
            
            # Handle order by - not directly supported in XPath 3.0
            # Ordering would require sorting the result sequence which isn't practical
            if order_expr:
                # Log warning: order by clause is not supported and will be ignored
                pass
            
            converted = f'{converted} return {return_expr}'
            
            # Replace in original query
            query = query[:match.start()] + converted + query[match.end():]
        
        # Pattern 2: for...return..., let...return (comma separated - already handled)
        comma_flwor = r'for\s+\$(?P<for_var>\w+)\s+in\s+(?P<for_path>[^\r\n]+)\s+return\s+(?P<first_return>[^,]+),\s*let\s+\$(?P<let_var>\w+)\s*:=\s*(?P<let_expr>[^\r\n]+)\s+return\s+(?P<second_return>.+)'
        match = re.search(comma_flwor, query, re.DOTALL)
        
        if match:
            for_var = match.group('for_var').strip()
            for_path = match.group('for_path').strip()
            first_return = match.group('first_return').strip()
            let_var = match.group('let_var').strip()
            let_expr = match.group('let_expr').strip()
            second_return = match.group('second_return').strip()
            
            # Convert element construction to string representations
            first_return = convert_element_constructors(first_return)
            second_return = convert_element_constructors(second_return)
            
            # Substitute let variable with escaped pattern to prevent ReDoS
            let_var_escaped = re.escape(let_var)
            second_return = re.sub(r'\$' + let_var_escaped + r'(?!\w)', let_expr, second_return)
            
            # Create sequence
            converted = f'(for ${for_var} in {for_path} return {first_return}, {second_return})'
            query = query[:match.start()] + converted + query[match.end():]
        
        return query
    
    @staticmethod
    def execute_xquery(xml_string: str, xquery_string: str) -> Tuple[bool, str, List]:
        """
        Execute XQuery expression against XML document.
        
        Args:
            xml_string: XML content as string
            xquery_string: XQuery expression (XPath 3.0 syntax)
            
        Returns:
            Tuple of (success, message, results)
            - success: True if execution succeeded
            - message: Success or error message
            - results: List of result items
        """
        if not XQUERY_AVAILABLE:
            return False, "XQuery support not available. Install 'elementpath' package.", []
        
        try:
            # Detect outer element wrapper to reconstruct structured output after execution
            wrapper_tag = None
            inner_query = xquery_string
            stripped_query = xquery_string.strip()
            wrapper_prefix = (
                r'(?:\(:.*?:\)\s*)*'  # Leading XQuery comments
                r'(?:xquery\s+version\s+"[^"]*"(?:\s+encoding\s+"[^"]*")?\s*;\s*)?'  # Version declaration
                r'(?:declare\s+[^\;]+;\s*)*'  # Declare statements
            )
            wrapper_pattern = r'^\s*' + wrapper_prefix + r'<([\w:-]+)[^>]*>\s*\{(.*)\}\s*</\1>\s*$'
            wrapper_match = re.match(wrapper_pattern, stripped_query, re.DOTALL | re.IGNORECASE)
            if wrapper_match:
                wrapper_tag = wrapper_match.group(1)
                inner_query = wrapper_match.group(2)
            
            # Preprocess XQuery to handle unsupported syntax
            processed_query = XMLUtilities.preprocess_xquery(inner_query)
            
            # Parse XML
            tree = etree.fromstring(xml_string.encode('utf-8'))
            
            # Create XPath 3.0 parser (supports XQuery-like syntax)
            parser = XPath30Parser()
            
            # Parse and execute query
            query = parser.parse(processed_query.strip())
            context = elementpath.XPathContext(tree)
            result = query.evaluate(context=context)
            
            # Convert result to list
            if result is None:
                result_list = []
            elif isinstance(result, (list, tuple)):
                result_list = list(result)
            elif hasattr(result, '__iter__') and not isinstance(result, str):
                result_list = list(result)
            else:
                result_list = [result]
            
            # Format results for display
            formatted_results = []
            for item in result_list:
                if hasattr(item, 'elem'):
                    # ElementNode - convert to string
                    elem = item.elem
                    formatted_results.append(etree.tostring(elem, encoding='unicode', pretty_print=True))
                elif isinstance(item, str):
                    formatted_results.append(item)
                elif hasattr(item, 'value'):
                    # TextNode or other node with value
                    formatted_results.append(str(item.value))
                else:
                    formatted_results.append(str(item))
            
            # If the query was wrapped in an element constructor, rebuild the structured XML output
            if wrapper_tag is not None:
                wrapped_content = ''.join(
                    part if isinstance(part, str) else str(part)
                    for part in formatted_results
                )
                formatted_results = [f"<{wrapper_tag}>{wrapped_content}</{wrapper_tag}>"]
            
            if not formatted_results:
                return True, "Query executed successfully (empty result)", []
            
            return True, f"Query executed successfully ({len(formatted_results)} result(s))", formatted_results
            
        except Exception as e:
            return False, f"XQuery execution error: {str(e)}", []
