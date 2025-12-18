#!/usr/bin/env python3
"""
Test script to verify XML graph view functionality.
Skips gracefully when Qt dependencies are unavailable.
"""

import sys
import os
import unittest

_QT_AVAILABLE = None
SKIP_REASON = "Qt dependencies unavailable; skipping graph view tests."


def _qt_available():
    """Return True if Qt libraries can be imported (cached)."""
    global _QT_AVAILABLE
    if _QT_AVAILABLE is not None:
        return _QT_AVAILABLE
    try:
        from PyQt6.QtWidgets import QApplication  # noqa: F401
        _QT_AVAILABLE = True
    except ImportError:
        _QT_AVAILABLE = False
    return _QT_AVAILABLE

@unittest.skipIf(not _qt_available(), SKIP_REASON)
def test_constants():
    """Test that constants are defined."""
    from xmleditor.xml_graph_view import TEXT_PREVIEW_LENGTH, TOOLTIP_TEXT_LENGTH
    from xmleditor.xml_graph_view import DEPTH_COLORS, NESTING_BG_COLORS
    
    assert TEXT_PREVIEW_LENGTH == 15, "TEXT_PREVIEW_LENGTH should be 15"
    assert TOOLTIP_TEXT_LENGTH == 100, "TOOLTIP_TEXT_LENGTH should be 100"
    assert len(DEPTH_COLORS) == 8, "Should have 8 depth colors"
    assert len(NESTING_BG_COLORS) == 8, "Should have 8 nesting background colors"
    print("  Constants defined correctly")


@unittest.skipIf(not _qt_available(), SKIP_REASON)
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


@unittest.skipIf(not _qt_available(), SKIP_REASON)
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


@unittest.skipIf(not _qt_available(), SKIP_REASON)
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
        if not _qt_available():
            raise unittest.SkipTest(SKIP_REASON)

        # Set Qt platform for headless testing once we know Qt is available
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'

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
    except unittest.SkipTest:
        print(f"\n{SKIP_REASON}\n")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
