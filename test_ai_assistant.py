#!/usr/bin/env python3
"""
Test script to verify AI Assistant agentic features.
"""

import pytest
from unittest.mock import MagicMock, patch
from xmleditor.ai_assistant import AIAssistantPanel, MarkdownRenderer


# Test XML content
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
    <book category="cooking">
        <title lang="en">Everyday Italian</title>
        <author>Giada De Laurentiis</author>
        <year>2005</year>
        <price>30.00</price>
    </book>
</bookstore>"""


class TestAIAssistantAgenticFeatures:
    """Test AI Assistant agentic capabilities."""
    
    @pytest.fixture
    def panel(self, qtbot):
        """Create an AIAssistantPanel for testing."""
        panel = AIAssistantPanel()
        qtbot.addWidget(panel)
        return panel
    
    def test_panel_has_agentic_signals(self, panel):
        """Test that the panel has all required agentic signals."""
        # Check signal existence
        assert hasattr(panel, 'request_apply_xml')
        assert hasattr(panel, 'request_open_file')
        assert hasattr(panel, 'request_format_xml')
        assert hasattr(panel, 'request_validate_xml')
    
    def test_execute_xpath_query(self, panel):
        """Test XPath query execution."""
        panel.set_xml_content(xml_content)
        
        # Test basic XPath query
        result = panel.execute_xpath_query("//book")
        assert "<book" in result
        assert "Learning XML" in result or "Everyday Italian" in result
        
        # Test count function
        result = panel.execute_xpath_query("count(//book)")
        assert "2" in result
        
        # Test attribute query
        result = panel.execute_xpath_query("//book/@category")
        assert "web" in result or "cooking" in result
    
    def test_execute_xpath_query_no_content(self, panel):
        """Test XPath query with no XML content."""
        panel.set_xml_content("")
        result = panel.execute_xpath_query("//book")
        assert "No XML content" in result
    
    def test_execute_xpath_query_invalid_expression(self, panel):
        """Test XPath query with invalid expression."""
        panel.set_xml_content(xml_content)
        result = panel.execute_xpath_query("///invalid[[[")
        assert "Error" in result
    
    def test_execute_validate_xml_valid(self, panel):
        """Test XML validation with valid XML."""
        panel.set_xml_content(xml_content)
        result = panel.execute_validate_xml()
        assert "✅" in result
        assert "well-formed" in result.lower()
    
    def test_execute_validate_xml_invalid(self, panel):
        """Test XML validation with invalid XML."""
        panel.set_xml_content("<root><unclosed>")
        result = panel.execute_validate_xml()
        assert "❌" in result
    
    def test_execute_validate_xml_no_content(self, panel):
        """Test XML validation with no content."""
        panel.set_xml_content("")
        result = panel.execute_validate_xml()
        assert "No XML content" in result
    
    def test_process_tool_commands_apply_xml(self, panel, qtbot):
        """Test processing [[APPLY_XML]] command."""
        panel.set_xml_content(xml_content)
        
        # Prepare a signal spy
        with qtbot.waitSignal(panel.request_apply_xml, timeout=1000) as blocker:
            response = """Let me fix that:

[[APPLY_XML]]
```xml
<root><fixed>content</fixed></root>
```

Done!"""
            processed = panel.process_tool_commands(response)
        
        assert blocker.signal_triggered
        assert "Applied XML to editor" in processed
    
    def test_process_tool_commands_xpath(self, panel):
        """Test processing [[XPATH:]] command."""
        panel.set_xml_content(xml_content)
        
        response = "Let me count the books: [[XPATH: count(//book)]]"
        processed = panel.process_tool_commands(response)
        
        assert "XPath" in processed
        assert "2" in processed
    
    def test_process_tool_commands_format_xml(self, panel, qtbot):
        """Test processing [[FORMAT_XML]] command."""
        with qtbot.waitSignal(panel.request_format_xml, timeout=1000):
            response = "I'll format your XML: [[FORMAT_XML]]"
            processed = panel.process_tool_commands(response)
        
        assert "Formatted XML" in processed
    
    def test_process_tool_commands_validate_xml(self, panel, qtbot):
        """Test processing [[VALIDATE_XML]] command."""
        panel.set_xml_content(xml_content)
        
        with qtbot.waitSignal(panel.request_validate_xml, timeout=1000):
            response = "Let me validate: [[VALIDATE_XML]]"
            processed = panel.process_tool_commands(response)
        
        assert "Validation" in processed
    
    def test_process_tool_commands_open_file(self, panel, qtbot):
        """Test processing [[OPEN_FILE:]] command."""
        with qtbot.waitSignal(panel.request_open_file, timeout=1000) as blocker:
            response = "Opening the file: [[OPEN_FILE: /path/to/file.xml]]"
            processed = panel.process_tool_commands(response)
        
        assert blocker.signal_triggered
        assert "Opened file" in processed
    
    def test_set_open_files_context(self, panel):
        """Test setting open files context."""
        files_info = [
            {'path': '/path/to/file1.xml', 'is_current': True},
            {'path': '/path/to/file2.xml', 'is_current': False},
        ]
        panel.set_open_files_context(files_info)
        assert panel.open_files_info == files_info
    
    def test_system_prompt_contains_agentic_info(self, panel):
        """Test that system prompt contains agentic features documentation."""
        prompt = panel.SYSTEM_PROMPT
        assert "[[APPLY_XML]]" in prompt
        assert "[[XPATH:" in prompt
        assert "[[FORMAT_XML]]" in prompt
        assert "[[VALIDATE_XML]]" in prompt
        assert "[[OPEN_FILE:" in prompt


class TestMarkdownRenderer:
    """Test Markdown rendering."""
    
    def test_render_user_message(self):
        """Test rendering user message."""
        html = MarkdownRenderer.render("Hello world", is_user=True)
        assert "user-message" in html
        assert "You:" in html
        assert "Hello world" in html
    
    def test_render_ai_message(self):
        """Test rendering AI message."""
        html = MarkdownRenderer.render("Hello world", is_user=False)
        assert "ai-message" in html
        assert "AI:" in html
        assert "Hello world" in html
    
    def test_render_code_block(self):
        """Test rendering code blocks."""
        text = "Here is code:\n```xml\n<root/>\n```"
        html = MarkdownRenderer.render(text, is_user=False)
        assert "code-block" in html
        assert "&lt;root/&gt;" in html  # HTML escaped
    
    def test_render_headers(self):
        """Test rendering headers."""
        text = "# Heading 1\n## Heading 2"
        html = MarkdownRenderer.render(text, is_user=False)
        assert "<h1>" in html
        assert "<h2>" in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
