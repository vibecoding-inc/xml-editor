"""
XML graph view widget for visualizing XML structure as a node graph.
Highlights parent-child relationships through visual nesting and connections.
Supports schema-based key/keyref reference highlighting.
"""

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, 
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
    QGraphicsEllipseItem, QWidget, QVBoxLayout, QGraphicsPathItem
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QPainterPath
from lxml import etree
from typing import List, Dict, Any, Optional, Tuple


# Constants for text truncation
TEXT_PREVIEW_LENGTH = 15
TOOLTIP_TEXT_LENGTH = 100

# Constants for key reference line layout
KEY_REF_CURVE_OFFSET = 50  # Vertical offset for reference line curves
KEY_REF_CURVE_CONTROL = 30  # Horizontal offset for curve control points

# Color for key reference lines (red/pink for visibility)
KEY_REFERENCE_COLOR = QColor(255, 50, 100)
KEY_NODE_HIGHLIGHT_COLOR = QColor(255, 215, 0)  # Gold for key nodes
KEYREF_NODE_HIGHLIGHT_COLOR = QColor(255, 100, 150)  # Pink for keyref nodes

# Color palette for different nesting depths (gradient from light to dark)
DEPTH_COLORS = [
    QColor(70, 130, 180),    # Steel blue (root)
    QColor(60, 179, 113),    # Medium sea green
    QColor(255, 165, 0),     # Orange
    QColor(186, 85, 211),    # Medium orchid
    QColor(220, 20, 60),     # Crimson
    QColor(0, 191, 255),     # Deep sky blue
    QColor(255, 215, 0),     # Gold
    QColor(147, 112, 219),   # Medium purple
]

# Background colors for nesting containers (very light versions)
NESTING_BG_COLORS = [
    QColor(230, 240, 250, 80),   # Light blue
    QColor(230, 250, 240, 80),   # Light green
    QColor(255, 245, 230, 80),   # Light orange
    QColor(250, 235, 255, 80),   # Light purple
    QColor(255, 235, 240, 80),   # Light red
    QColor(230, 250, 255, 80),   # Light cyan
    QColor(255, 250, 230, 80),   # Light gold
    QColor(245, 240, 255, 80),   # Light violet
]


class NestingContainer(QGraphicsRectItem):
    """A visual container that groups child nodes to show nesting relationship."""
    
    def __init__(self, depth: int = 0, parent_item: QGraphicsItem = None):
        super().__init__(parent_item)
        self.depth = depth
        
        # Set up appearance based on depth
        color_index = depth % len(NESTING_BG_COLORS)
        bg_color = NESTING_BG_COLORS[color_index]
        border_color = DEPTH_COLORS[color_index]
        
        self.setBrush(QBrush(bg_color))
        self.setPen(QPen(border_color, 1, Qt.PenStyle.DashLine))
        self.setZValue(-depth - 1)  # Behind nodes at same depth


class XMLNodeItem(QGraphicsRectItem):
    """A graphical item representing an XML node."""
    
    def __init__(self, tag: str, text: str = "", attributes: Dict[str, str] = None, 
                 depth: int = 0, parent_item: QGraphicsItem = None):
        super().__init__(parent_item)
        self.tag = tag
        self.text_content = text
        self.attributes = attributes or {}
        self.child_nodes: List['XMLNodeItem'] = []
        self.parent_node: Optional['XMLNodeItem'] = None
        self.depth = depth
        self.nesting_container: Optional[NestingContainer] = None
        self.is_key = False  # Flag for key elements
        self.is_keyref = False  # Flag for keyref elements
        self.xpath: str = ""  # Store XPath for matching
        
        # Set up appearance based on depth
        color_index = depth % len(DEPTH_COLORS)
        node_color = DEPTH_COLORS[color_index]
        border_color = node_color.darker(130)
        
        self._base_color = node_color
        self._border_color = border_color
        
        self.setRect(0, 0, 120, 60)
        self.setBrush(QBrush(node_color))
        self.setPen(QPen(border_color, 2))
        
        # Add depth indicator
        depth_indicator = QGraphicsTextItem(f"L{depth}", self)
        depth_indicator.setDefaultTextColor(QColor(255, 255, 255, 150))
        depth_font = QFont("Arial", 7)
        depth_indicator.setFont(depth_font)
        depth_indicator.setPos(3, 3)
        
        # Add tag name text
        self.tag_text = QGraphicsTextItem(tag, self)
        self.tag_text.setDefaultTextColor(QColor(255, 255, 255))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.tag_text.setFont(font)
        
        # Center the text
        text_rect = self.tag_text.boundingRect()
        self.tag_text.setPos(
            (120 - text_rect.width()) / 2,
            15
        )
        
        # Add text content preview if available
        if text:
            preview = text[:TEXT_PREVIEW_LENGTH] + "..." if len(text) > TEXT_PREVIEW_LENGTH else text
            self.content_text = QGraphicsTextItem(preview, self)
            self.content_text.setDefaultTextColor(QColor(220, 220, 220))
            content_font = QFont("Arial", 8)
            self.content_text.setFont(content_font)
            content_rect = self.content_text.boundingRect()
            self.content_text.setPos(
                (120 - content_rect.width()) / 2,
                32
            )
        
        # Add attribute indicator if has attributes
        if attributes:
            attr_count = len(attributes)
            attr_text = f"[{attr_count} attr{'s' if attr_count > 1 else ''}]"
            self.attr_text = QGraphicsTextItem(attr_text, self)
            self.attr_text.setDefaultTextColor(QColor(200, 200, 100))
            attr_font = QFont("Arial", 7)
            self.attr_text.setFont(attr_font)
            attr_rect = self.attr_text.boundingRect()
            self.attr_text.setPos(
                (120 - attr_rect.width()) / 2,
                46
            )
        
        # Make item movable and selectable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        
        # Set Z value based on depth (higher depth = on top)
        self.setZValue(depth)
        
        # Store tooltip with full information
        tooltip = f"Tag: {tag}\nDepth: {depth}"
        if text:
            tooltip += f"\nText: {text[:TOOLTIP_TEXT_LENGTH]}{'...' if len(text) > TOOLTIP_TEXT_LENGTH else ''}"
        if attributes:
            tooltip += "\nAttributes:"
            for k, v in attributes.items():
                tooltip += f"\n  {k}={v}"
        self.setToolTip(tooltip)
    
    def set_as_key(self):
        """Mark this node as a key element."""
        self.is_key = True
        self.setBrush(QBrush(KEY_NODE_HIGHLIGHT_COLOR))
        self.setPen(QPen(KEY_NODE_HIGHLIGHT_COLOR.darker(130), 3))
        # Update tooltip
        current_tooltip = self.toolTip()
        self.setToolTip(current_tooltip + "\n\n🔑 KEY ELEMENT")
    
    def set_as_keyref(self):
        """Mark this node as a keyref element."""
        self.is_keyref = True
        self.setBrush(QBrush(KEYREF_NODE_HIGHLIGHT_COLOR))
        self.setPen(QPen(KEYREF_NODE_HIGHLIGHT_COLOR.darker(130), 3))
        # Update tooltip
        current_tooltip = self.toolTip()
        self.setToolTip(current_tooltip + "\n\n🔗 KEY REFERENCE")
    
    def get_center_bottom(self) -> QPointF:
        """Get the center bottom point of this node."""
        rect = self.sceneBoundingRect()
        return QPointF(rect.center().x(), rect.bottom())
    
    def get_center_top(self) -> QPointF:
        """Get the center top point of this node."""
        rect = self.sceneBoundingRect()
        return QPointF(rect.center().x(), rect.top())
    
    def get_center_right(self) -> QPointF:
        """Get the center right point of this node."""
        rect = self.sceneBoundingRect()
        return QPointF(rect.right(), rect.center().y())
    
    def get_center_left(self) -> QPointF:
        """Get the center left point of this node."""
        rect = self.sceneBoundingRect()
        return QPointF(rect.left(), rect.center().y())


class ConnectionLine(QGraphicsPathItem):
    """A curved line connecting parent and child nodes with arrow."""
    
    def __init__(self, parent_node: XMLNodeItem, child_node: XMLNodeItem):
        super().__init__()
        self.parent_node = parent_node
        self.child_node = child_node
        
        # Set up appearance - color based on parent depth
        color_index = parent_node.depth % len(DEPTH_COLORS)
        line_color = DEPTH_COLORS[color_index].darker(110)
        self.setPen(QPen(line_color, 2))
        
        # Set Z value below nodes
        self.setZValue(-0.5)
        
        self.update_position()
    
    def update_position(self):
        """Update line position based on connected nodes."""
        start = self.parent_node.get_center_bottom()
        end = self.child_node.get_center_top()
        
        # Create a curved path
        path = QPainterPath()
        path.moveTo(start)
        
        # Control points for bezier curve
        mid_y = (start.y() + end.y()) / 2
        path.cubicTo(
            start.x(), mid_y,
            end.x(), mid_y,
            end.x(), end.y()
        )
        
        self.setPath(path)


class KeyReferenceLine(QGraphicsPathItem):
    """A dashed curved line showing key-keyref reference relationship."""
    
    def __init__(self, key_node: XMLNodeItem, keyref_node: XMLNodeItem, key_name: str = ""):
        super().__init__()
        self.key_node = key_node
        self.keyref_node = keyref_node
        self.key_name = key_name
        
        # Set up appearance - red/pink dashed line for key references
        pen = QPen(KEY_REFERENCE_COLOR, 3, Qt.PenStyle.DashLine)
        self.setPen(pen)
        
        # Set Z value above regular connections but below nodes
        self.setZValue(0.5)
        
        # Set tooltip
        self.setToolTip(f"Key Reference: {key_name}\n{keyref_node.tag} → {key_node.tag}")
        
        self.update_position()
    
    def update_position(self):
        """Update line position based on connected nodes."""
        # Connect from keyref to key (showing direction of reference)
        start = self.keyref_node.get_center_right()
        end = self.key_node.get_center_left()
        
        # Create a curved path that goes around other elements
        path = QPainterPath()
        path.moveTo(start)
        
        # Calculate control points for a curved path
        # Curve upward if keyref is below key, downward otherwise
        if start.y() > end.y():
            control_y = min(start.y(), end.y()) - KEY_REF_CURVE_OFFSET
        else:
            control_y = max(start.y(), end.y()) + KEY_REF_CURVE_OFFSET
        
        path.cubicTo(
            start.x() + KEY_REF_CURVE_CONTROL, control_y,
            end.x() - KEY_REF_CURVE_CONTROL, control_y,
            end.x(), end.y()
        )
        
        self.setPath(path)


class XMLGraphScene(QGraphicsScene):
    """Scene for displaying XML as a node graph with nesting visualization."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes: List[XMLNodeItem] = []
        self.connections: List[ConnectionLine] = []
        self.key_references: List[KeyReferenceLine] = []
        self.nesting_containers: List[NestingContainer] = []
        self.node_width = 120
        self.node_height = 60
        self.horizontal_spacing = 40
        self.vertical_spacing = 80
        self.nesting_padding = 15  # Padding for nesting containers
        self.schema_content: Optional[str] = None  # Store schema for key analysis
        self.layout_algorithm: str = "tree_vertical"  # Default layout
    
    def set_layout_algorithm(self, algorithm: str):
        """Set the layout algorithm to use."""
        self.layout_algorithm = algorithm
    
    def clear_graph(self):
        """Clear all nodes and connections from the scene."""
        self.clear()
        self.nodes = []
        self.connections = []
        self.key_references = []
        self.nesting_containers = []
    
    def load_xml(self, xml_content: str, show_namespaces: bool = False, 
                 schema_content: Optional[str] = None):
        """
        Load XML content and create the node graph with nesting visualization.
        
        Args:
            xml_content: XML string to visualize
            show_namespaces: Whether to show namespace prefixes
            schema_content: Optional XSD schema content for key/keyref analysis
        """
        self.clear_graph()
        self.schema_content = schema_content
        
        try:
            tree = etree.fromstring(xml_content.encode('utf-8'))
            
            # Build the graph
            root_node = self._create_node_recursive(tree, show_namespaces, 0, tree)
            
            # Calculate layout based on selected algorithm
            if self.layout_algorithm == "tree_horizontal":
                self._layout_tree_horizontal(root_node, 0, 0)
            elif self.layout_algorithm == "radial":
                self._layout_radial(root_node)
            elif self.layout_algorithm == "compact":
                self._layout_compact(root_node, 0, 0)
            else:  # Default: tree_vertical
                self._layout_tree(root_node, 0, 0)
            
            # Create connection lines
            self._create_connections(root_node)
            
            # Create nesting containers to highlight parent-child relationships
            self._create_nesting_containers(root_node)
            
            # If schema provided, parse and highlight key references
            if schema_content:
                self._apply_key_references(tree, schema_content)
            
            # Adjust scene rect to fit all items
            self.setSceneRect(self.itemsBoundingRect().adjusted(-50, -50, 50, 50))
            
        except Exception as e:
            # Show error message in scene
            error_text = self.addText(f"Error: {str(e)}")
            error_text.setDefaultTextColor(QColor(255, 0, 0))
    
    def _apply_key_references(self, xml_tree: etree._Element, schema_content: str):
        """Parse schema and apply key/keyref highlighting to nodes."""
        try:
            schema_tree = etree.fromstring(schema_content.encode('utf-8'))
            
            # XSD namespace
            xs_ns = '{http://www.w3.org/2001/XMLSchema}'
            
            # Find all key and keyref definitions
            keys = {}  # name -> {selector_xpath, field_xpath}
            keyrefs = []  # list of {name, refer, selector_xpath, field_xpath}
            
            for key_elem in schema_tree.iter(f'{xs_ns}key'):
                key_name = key_elem.get('name')
                selector = key_elem.find(f'{xs_ns}selector')
                field = key_elem.find(f'{xs_ns}field')
                if key_name and selector is not None and field is not None:
                    keys[key_name] = {
                        'selector': selector.get('xpath', ''),
                        'field': field.get('xpath', '')
                    }
            
            for keyref_elem in schema_tree.iter(f'{xs_ns}keyref'):
                keyref_name = keyref_elem.get('name')
                refer = keyref_elem.get('refer')
                selector = keyref_elem.find(f'{xs_ns}selector')
                field = keyref_elem.find(f'{xs_ns}field')
                if keyref_name and refer and selector is not None and field is not None:
                    keyrefs.append({
                        'name': keyref_name,
                        'refer': refer,
                        'selector': selector.get('xpath', ''),
                        'field': field.get('xpath', '')
                    })
            
            # Build a mapping from XPath to graph nodes
            node_map = self._build_node_map()
            
            # Apply key highlighting
            for key_name, key_info in keys.items():
                selector_xpath = key_info['selector']
                field_xpath = key_info['field']
                
                # Find elements matching the selector
                try:
                    key_elements = xml_tree.xpath(selector_xpath)
                    for elem in key_elements:
                        # Find the field value
                        field_values = elem.xpath(field_xpath)
                        
                        # Find corresponding graph node and mark as key
                        elem_path = xml_tree.getroottree().getpath(elem)
                        if elem_path in node_map:
                            node_map[elem_path].set_as_key()
                            
                        # Also mark the field element if it's a child element
                        if field_xpath.startswith('@'):
                            # It's an attribute, the key is on the element itself
                            pass
                        else:
                            # It's a child element
                            for field_elem in elem.xpath(field_xpath):
                                if hasattr(field_elem, 'getroottree'):
                                    field_path = xml_tree.getroottree().getpath(field_elem)
                                    if field_path in node_map:
                                        node_map[field_path].set_as_key()
                except etree.XPathEvalError:
                    pass  # Skip if XPath evaluation fails
                except Exception:
                    pass  # Skip other errors
            
            # Apply keyref highlighting and create reference lines
            for keyref_info in keyrefs:
                ref_name = keyref_info['refer']
                if ref_name not in keys:
                    continue
                    
                key_info = keys[ref_name]
                selector_xpath = keyref_info['selector']
                field_xpath = keyref_info['field']
                
                try:
                    # Find keyref elements
                    keyref_elements = xml_tree.xpath(selector_xpath)
                    
                    for keyref_elem in keyref_elements:
                        # Get the field value (the reference value)
                        field_values = keyref_elem.xpath(field_xpath)
                        
                        keyref_elem_path = xml_tree.getroottree().getpath(keyref_elem)
                        
                        # Mark the keyref element
                        if keyref_elem_path in node_map:
                            node_map[keyref_elem_path].set_as_keyref()
                        
                        # Also mark the field element
                        for field_elem in keyref_elem.xpath(field_xpath):
                            if hasattr(field_elem, 'getroottree'):
                                field_path = xml_tree.getroottree().getpath(field_elem)
                                if field_path in node_map:
                                    keyref_node = node_map[field_path]
                                    keyref_node.set_as_keyref()
                                    
                                    # Get the reference value (handle None text)
                                    ref_value = field_elem.text if field_elem.text is not None else ""
                                    
                                    # Find the matching key element
                                    key_selector = key_info['selector']
                                    key_field = key_info['field']
                                    
                                    for key_elem in xml_tree.xpath(key_selector):
                                        key_values = key_elem.xpath(key_field)
                                        for kv in key_values:
                                            # Handle both string results and element results
                                            if isinstance(kv, str):
                                                kv_text = kv
                                            elif hasattr(kv, 'text') and kv.text is not None:
                                                kv_text = kv.text
                                            else:
                                                kv_text = str(kv) if kv is not None else ""
                                            
                                            if kv_text == ref_value and ref_value:
                                                key_elem_path = xml_tree.getroottree().getpath(key_elem)
                                                if key_elem_path in node_map:
                                                    key_node = node_map[key_elem_path]
                                                    # Create reference line
                                                    ref_line = KeyReferenceLine(
                                                        key_node, keyref_node, 
                                                        keyref_info['name']
                                                    )
                                                    self.addItem(ref_line)
                                                    self.key_references.append(ref_line)
                except etree.XPathEvalError:
                    pass  # Skip if XPath evaluation fails
                except Exception:
                    pass  # Skip other XPath-related errors
                    
        except etree.XMLSyntaxError:
            pass  # Schema parsing error - don't break the graph
        except Exception:
            pass  # Other schema errors - silently continue
    
    def _build_node_map(self) -> Dict[str, XMLNodeItem]:
        """Build a mapping from XPath to graph nodes."""
        node_map = {}
        for node in self.nodes:
            if node.xpath:
                node_map[node.xpath] = node
        return node_map
    
    def _extract_tag_name(self, element: etree._Element, show_namespaces: bool) -> str:
        """Extract the tag name from an element, handling namespaces."""
        tag = element.tag
        if isinstance(tag, str) and tag.startswith('{') and '}' in tag:
            parts = tag[1:].split('}', 1)
            if len(parts) == 2:
                ns_uri, local_name = parts
                if show_namespaces:
                    prefix = None
                    for p, uri in element.nsmap.items():
                        if uri == ns_uri:
                            prefix = p
                            break
                    return f"{prefix}:{local_name}" if prefix else local_name
                return local_name
        return tag
    
    def _create_node_recursive(self, element: etree._Element, 
                                show_namespaces: bool, depth: int,
                                root_tree: etree._Element = None) -> XMLNodeItem:
        """Recursively create nodes for the XML tree."""
        tag = self._extract_tag_name(element, show_namespaces)
        text = element.text.strip() if element.text and element.text.strip() else ""
        attributes = dict(element.attrib)
        
        node = XMLNodeItem(tag, text, attributes, depth)
        
        # Store XPath for this node
        if root_tree is None:
            root_tree = element
        try:
            node.xpath = root_tree.getroottree().getpath(element)
        except Exception:
            node.xpath = ""
        
        self.addItem(node)
        self.nodes.append(node)
        
        # Process children
        for child_element in element:
            child_node = self._create_node_recursive(child_element, show_namespaces, depth + 1, root_tree)
            child_node.parent_node = node
            node.child_nodes.append(child_node)
        
        return node
    
    def _calculate_position(self, offset: int, depth: int) -> tuple:
        """Calculate x, y position based on offset and depth."""
        x = offset * (self.node_width + self.horizontal_spacing)
        y = depth * (self.node_height + self.vertical_spacing)
        return x, y
    
    def _layout_tree(self, node: XMLNodeItem, depth: int, offset: int) -> int:
        """
        Layout the tree using a simple recursive algorithm (top-down).
        Returns the width taken by this subtree.
        """
        if not node.child_nodes:
            # Leaf node
            x, y = self._calculate_position(offset, depth)
            node.setPos(x, y)
            return 1
        
        # Calculate positions for children
        child_width = 0
        for child in node.child_nodes:
            child_width += self._layout_tree(child, depth + 1, offset + child_width)
        
        # Position this node centered above its children
        first_child_x = node.child_nodes[0].pos().x()
        last_child_x = node.child_nodes[-1].pos().x()
        center_x = (first_child_x + last_child_x) / 2
        
        _, y = self._calculate_position(0, depth)
        node.setPos(center_x, y)
        
        return child_width
    
    def _layout_tree_horizontal(self, node: XMLNodeItem, depth: int, offset: int) -> int:
        """
        Layout the tree horizontally (left-to-right).
        Returns the height taken by this subtree.
        """
        if not node.child_nodes:
            # Leaf node - swap x and y
            x = depth * (self.node_width + self.horizontal_spacing)
            y = offset * (self.node_height + self.vertical_spacing // 2)
            node.setPos(x, y)
            return 1
        
        # Calculate positions for children
        child_height = 0
        for child in node.child_nodes:
            child_height += self._layout_tree_horizontal(child, depth + 1, offset + child_height)
        
        # Position this node centered to the left of its children
        first_child_y = node.child_nodes[0].pos().y()
        last_child_y = node.child_nodes[-1].pos().y()
        center_y = (first_child_y + last_child_y) / 2
        
        x = depth * (self.node_width + self.horizontal_spacing)
        node.setPos(x, center_y)
        
        return child_height
    
    def _layout_radial(self, root_node: XMLNodeItem):
        """
        Layout the tree in a radial/circular pattern.
        """
        import math
        
        # Calculate total nodes at each level for angle distribution
        def count_leaves(node: XMLNodeItem) -> int:
            if not node.child_nodes:
                return 1
            return sum(count_leaves(c) for c in node.child_nodes)
        
        total_leaves = count_leaves(root_node)
        if total_leaves == 0:
            total_leaves = 1
        
        # Center position
        center_x = 400
        center_y = 400
        radius_step = 150
        
        # Position root at center
        root_node.setPos(center_x - self.node_width / 2, center_y - self.node_height / 2)
        
        def layout_radial_recursive(node: XMLNodeItem, start_angle: float, 
                                    end_angle: float, depth: int):
            if not node.child_nodes:
                return
            
            radius = depth * radius_step
            total_child_leaves = sum(count_leaves(c) for c in node.child_nodes)
            if total_child_leaves == 0:
                total_child_leaves = len(node.child_nodes)
            
            angle_range = end_angle - start_angle
            current_angle = start_angle
            
            for child in node.child_nodes:
                child_leaves = count_leaves(child)
                child_angle_span = (child_leaves / total_child_leaves) * angle_range
                child_angle = current_angle + child_angle_span / 2
                
                # Calculate position
                x = center_x + radius * math.cos(child_angle) - self.node_width / 2
                y = center_y + radius * math.sin(child_angle) - self.node_height / 2
                child.setPos(x, y)
                
                # Recurse for children
                layout_radial_recursive(child, current_angle, 
                                       current_angle + child_angle_span, depth + 1)
                
                current_angle += child_angle_span
        
        # Start layout from root
        layout_radial_recursive(root_node, 0, 2 * math.pi, 1)
    
    def _layout_compact(self, node: XMLNodeItem, depth: int, offset: int) -> int:
        """
        Layout the tree in a more compact form with reduced spacing.
        Returns the width taken by this subtree.
        """
        # Use reduced spacing for compact layout
        compact_h_spacing = 20
        compact_v_spacing = 50
        
        if not node.child_nodes:
            # Leaf node
            x = offset * (self.node_width + compact_h_spacing)
            y = depth * (self.node_height + compact_v_spacing)
            node.setPos(x, y)
            return 1
        
        # Calculate positions for children
        child_width = 0
        for child in node.child_nodes:
            child_width += self._layout_compact(child, depth + 1, offset + child_width)
        
        # Position this node centered above its children
        first_child_x = node.child_nodes[0].pos().x()
        last_child_x = node.child_nodes[-1].pos().x()
        center_x = (first_child_x + last_child_x) / 2
        
        y = depth * (self.node_height + compact_v_spacing)
        node.setPos(center_x, y)
        
        return child_width
    
    def _create_connections(self, node: XMLNodeItem):
        """Create connection lines between nodes."""
        for child in node.child_nodes:
            connection = ConnectionLine(node, child)
            self.addItem(connection)
            self.connections.append(connection)
            self._create_connections(child)
    
    def _create_nesting_containers(self, node: XMLNodeItem):
        """Create nesting containers to visually group parent and children."""
        if node.child_nodes:
            # Calculate bounding rect for all descendants
            bounds = self._get_subtree_bounds(node)
            
            # Add padding
            padded_bounds = bounds.adjusted(
                -self.nesting_padding, 
                -self.nesting_padding,
                self.nesting_padding, 
                self.nesting_padding
            )
            
            # Create container
            container = NestingContainer(node.depth)
            container.setRect(padded_bounds)
            self.addItem(container)
            self.nesting_containers.append(container)
            node.nesting_container = container
            
            # Recursively create containers for children with children
            for child in node.child_nodes:
                self._create_nesting_containers(child)
    
    def _get_subtree_bounds(self, node: XMLNodeItem) -> QRectF:
        """Get the bounding rectangle of a node and all its descendants."""
        # Start with this node's bounds
        bounds = node.sceneBoundingRect()
        
        # Expand to include all children
        for child in node.child_nodes:
            child_bounds = self._get_subtree_bounds(child)
            bounds = bounds.united(child_bounds)
        
        return bounds


class XMLGraphView(QGraphicsView):
    """View widget for displaying the XML graph."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph_scene = XMLGraphScene()
        self.setScene(self.graph_scene)
        self.schema_content: Optional[str] = None  # Store schema for key highlighting
        self.layout_algorithm: str = "tree_vertical"  # Current layout algorithm
        
        # Display options
        self.show_connections = True
        self.show_nesting = True
        self.show_keyrefs = True
        
        # Set up view properties
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Enable zooming
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Set background
        self.setBackgroundBrush(QBrush(QColor(245, 245, 250)))
        
        # Minimum size
        self.setMinimumSize(300, 150)
    
    def set_schema(self, schema_content: Optional[str]):
        """Set the XSD schema content for key/keyref highlighting."""
        self.schema_content = schema_content
    
    def set_layout_algorithm(self, algorithm: str):
        """Set the layout algorithm to use."""
        self.layout_algorithm = algorithm
        self.graph_scene.set_layout_algorithm(algorithm)
    
    def set_display_options(self, show_connections: bool = True, 
                           show_nesting: bool = True, show_keyrefs: bool = True):
        """Set display options for graph elements."""
        self.show_connections = show_connections
        self.show_nesting = show_nesting
        self.show_keyrefs = show_keyrefs
        
        # Update visibility of elements
        for conn in self.graph_scene.connections:
            conn.setVisible(show_connections)
        for container in self.graph_scene.nesting_containers:
            container.setVisible(show_nesting)
        for keyref in self.graph_scene.key_references:
            keyref.setVisible(show_keyrefs)
    
    def load_xml(self, xml_content: str, show_namespaces: bool = False):
        """Load XML content and display as a graph."""
        self.graph_scene.load_xml(xml_content, show_namespaces, self.schema_content)
        # Apply current display options
        self.set_display_options(self.show_connections, self.show_nesting, self.show_keyrefs)
        self.fitInView(self.graph_scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def clear(self):
        """Clear the graph view."""
        self.graph_scene.clear_graph()
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        # Zoom factor
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # Get the wheel delta
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        
        self.scale(zoom_factor, zoom_factor)
    
    def fit_to_view(self):
        """Fit the entire graph in the view."""
        if self.graph_scene.nodes:
            self.fitInView(self.graph_scene.sceneRect(), 
                          Qt.AspectRatioMode.KeepAspectRatio)
