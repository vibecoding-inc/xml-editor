"""
XML tree view widget for visualizing XML structure.
"""

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from xmleditor.xml_utils import XMLUtilities


class XMLTreeView(QTreeWidget):
    """Tree widget for displaying XML structure."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Element", "Value", "Attributes"])
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 150)
        self.setAlternatingRowColors(True)
        
    def load_xml(self, xml_content: str):
        """
        Load XML content into tree view.
        
        Args:
            xml_content: XML string to display
        """
        self.clear()
        
        try:
            tree_structure = XMLUtilities.get_xml_tree_structure(xml_content)
            
            for node in tree_structure:
                self.add_node(None, node)
                
            self.expandToDepth(1)
        except Exception as e:
            error_item = QTreeWidgetItem(self)
            error_item.setText(0, f"Error: {str(e)}")
            error_item.setForeground(0, Qt.GlobalColor.red)
    
    def add_node(self, parent_item, node: dict):
        """
        Recursively add nodes to tree.
        
        Args:
            parent_item: Parent tree widget item
            node: Node dictionary
        """
        if parent_item is None:
            item = QTreeWidgetItem(self)
        else:
            item = QTreeWidgetItem(parent_item)
        
        # Set tag name
        item.setText(0, node['tag'])
        
        # Set text content
        if node['text']:
            item.setText(1, node['text'][:50] + ('...' if len(node['text']) > 50 else ''))
            item.setToolTip(1, node['text'])
        
        # Set attributes
        if node['attributes']:
            attr_text = ', '.join([f"{k}={v}" for k, v in node['attributes'].items()])
            item.setText(2, attr_text[:50] + ('...' if len(attr_text) > 50 else ''))
            item.setToolTip(2, attr_text)
        
        # Add children
        for child in node['children']:
            self.add_node(item, child)
