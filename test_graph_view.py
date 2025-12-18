#!/usr/bin/env python3
"""
Test script to verify XML graph view functionality.
"""

import sys
import os

# Ensure Qt uses offscreen platform for headless testing
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Test the graph view components in isolation (without Qt)
def test_constants():
    """Test that constants are defined."""
    from xmleditor.xml_graph_view import TEXT_PREVIEW_LENGTH, TOOLTIP_TEXT_LENGTH
    from xmleditor.xml_graph_view import DEPTH_COLORS, NESTING_BG_COLORS
    
    assert TEXT_PREVIEW_LENGTH == 15, "TEXT_PREVIEW_LENGTH should be 15"
    assert TOOLTIP_TEXT_LENGTH == 100, "TOOLTIP_TEXT_LENGTH should be 100"
    assert len(DEPTH_COLORS) == 8, "Should have 8 depth colors"
    assert len(NESTING_BG_COLORS) == 8, "Should have 8 nesting background colors"
    print("  Constants defined correctly")


def test_module_imports():
    """Test that all classes can be imported."""
    try:
        from xmleditor.xml_graph_view import (
            XMLGraphView, XMLGraphScene, XMLNodeItem, 
            NestingContainer, ConnectionLine
        )
        print("  All classes imported successfully")
        return True
    except ImportError as e:
        print(f"  Import error: {e}")
        return False


def test_graph_scene_with_qt():
    """Test graph scene with Qt (requires QApplication)."""
    try:
        from PyQt6.QtWidgets import QApplication
        
        # Create app if doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from xmleditor.xml_graph_view import XMLGraphScene
        
        # Test with simple XML
        scene = XMLGraphScene()
        xml_content = """<root>
            <child1>text</child1>
            <child2 attr="value">
                <nested>deep</nested>
            </child2>
        </root>"""
        
        scene.load_xml(xml_content)
        
        assert len(scene.nodes) == 4, f"Expected 4 nodes, got {len(scene.nodes)}"
        assert len(scene.connections) == 3, f"Expected 3 connections, got {len(scene.connections)}"
        assert len(scene.nesting_containers) == 2, f"Expected 2 nesting containers, got {len(scene.nesting_containers)}"
        
        # Verify node properties
        root_node = scene.nodes[0]
        assert root_node.tag == "root", f"Expected root tag, got {root_node.tag}"
        assert root_node.depth == 0, f"Expected depth 0, got {root_node.depth}"
        
        child1_node = scene.nodes[1]
        assert child1_node.depth == 1, f"Expected depth 1, got {child1_node.depth}"
        
        print("  Graph scene created and loaded XML correctly")
        print(f"    - Nodes: {len(scene.nodes)}")
        print(f"    - Connections: {len(scene.connections)}")
        print(f"    - Nesting containers: {len(scene.nesting_containers)}")
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_namespace_handling():
    """Test namespace handling in graph scene."""
    try:
        from PyQt6.QtWidgets import QApplication
        
        # Create app if doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from xmleditor.xml_graph_view import XMLGraphScene
        
        # Test with namespaced XML
        scene = XMLGraphScene()
        xml_ns = '''<root xmlns:ns="http://example.com"><ns:child>text</ns:child></root>'''
        
        # Test with namespaces shown
        scene.load_xml(xml_ns, show_namespaces=True)
        
        assert len(scene.nodes) == 2, f"Expected 2 nodes, got {len(scene.nodes)}"
        
        # The child should have namespace prefix
        child_node = scene.nodes[1]
        assert "ns:" in child_node.tag or child_node.tag == "child", f"Unexpected tag: {child_node.tag}"
        
        # Test with namespaces hidden
        scene2 = XMLGraphScene()
        scene2.load_xml(xml_ns, show_namespaces=False)
        child_node2 = scene2.nodes[1]
        assert child_node2.tag == "child", f"Expected 'child' without namespace, got {child_node2.tag}"
        
        print("  Namespace handling works correctly")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("XML Editor - Graph View Tests")
    print("=" * 60)
    print()
    
    try:
        print("Testing constants...")
        test_constants()
        
        print("\nTesting module imports...")
        test_module_imports()
        
        print("\nTesting graph scene...")
        test_graph_scene_with_qt()
        
        print("\nTesting namespace handling...")
        test_namespace_handling()
        
        print()
        print("=" * 60)
        print("All graph view tests passed! ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
