"""
XML tree view widget for visualizing XML structure.
"""

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
from xmleditor.xml_utils import XMLUtilities


class XMLTreeView(QTreeWidget):
    """Tree widget for displaying XML structure."""
    
    # Signal emitted when a node is selected, provides the XPath of the selected node
    nodeSelected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Element", "Value", "Attributes"])
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 150)
        self.setAlternatingRowColors(True)
        
        # Connect selection change signal
        self.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _on_selection_changed(self):
        """Handle selection change and emit nodeSelected signal with XPath."""
        selected_items = self.selectedItems()
        if selected_items:
            xpath = self._get_xpath_for_item(selected_items[0])
            self.nodeSelected.emit(xpath)
        else:
            self.nodeSelected.emit("")
    
    def _get_xpath_for_item(self, item: QTreeWidgetItem) -> str:
        """
        Build XPath expression for the given tree item.
        
        Args:
            item: Tree widget item
            
        Returns:
            XPath expression to select this element
        """
        path_parts = []
        current_item = item
        
        while current_item is not None:
            tag_name = current_item.text(0)
            
            # Check if there are siblings with the same tag name
            parent = current_item.parent()
            if parent is not None:
                # Count siblings with same tag name and find position
                same_tag_count = 0
                position = 0
                for i in range(parent.childCount()):
                    sibling = parent.child(i)
                    if sibling.text(0) == tag_name:
                        same_tag_count += 1
                        if sibling == current_item:
                            position = same_tag_count
                
                # Add position predicate if there are multiple siblings with same tag
                if same_tag_count > 1:
                    path_parts.insert(0, f"{tag_name}[{position}]")
                else:
                    path_parts.insert(0, tag_name)
            else:
                # Root element - check if there are multiple roots (shouldn't happen in valid XML)
                root_index = self.indexOfTopLevelItem(current_item)
                if self.topLevelItemCount() > 1:
                    path_parts.insert(0, f"{tag_name}[{root_index + 1}]")
                else:
                    path_parts.insert(0, tag_name)
            
            current_item = parent
        
        return "/" + "/".join(path_parts)
    
    def get_selected_xpath(self) -> str:
        """
        Get the XPath of the currently selected node.
        
        Returns:
            XPath expression for selected node, or empty string if nothing selected
        """
        selected_items = self.selectedItems()
        if selected_items:
            return self._get_xpath_for_item(selected_items[0])
        return ""
        
    def load_xml(self, xml_content: str, show_namespaces: bool = False):
        """
        Load XML content into tree view.
        
        Args:
            xml_content: XML string to display
            show_namespaces: Whether to show namespace prefixes in tag names
        """
        self.clear()
        
        try:
            tree_structure = XMLUtilities.get_xml_tree_structure(xml_content, show_namespaces)
            
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
