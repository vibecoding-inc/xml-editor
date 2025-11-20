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
    def get_xml_tree_structure(xml_string: str) -> List[dict]:
        """
        Get XML tree structure for tree view.
        
        Args:
            xml_string: XML content as string
            
        Returns:
            List of dictionaries representing tree nodes
        """
        try:
            tree = etree.fromstring(xml_string.encode('utf-8'))
            
            def element_to_dict(element):
                node = {
                    'tag': element.tag,
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
