"""
XML utilities for parsing, validating, and manipulating XML documents.
"""

from lxml import etree
import xml.dom.minidom
from typing import Optional, List, Tuple


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
    def xpath_query(xml_string: str, xpath_expr: str) -> List[str]:
        """
        Execute XPath query on XML.
        
        Args:
            xml_string: XML content as string
            xpath_expr: XPath expression
            
        Returns:
            List of matching results as strings
        """
        try:
            tree = etree.fromstring(xml_string.encode('utf-8'))
            results = tree.xpath(xpath_expr)
            
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
