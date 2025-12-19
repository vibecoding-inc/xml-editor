#!/usr/bin/env python3
"""
Test script for AI agent tools functionality.
"""

from xmleditor.ai_agent_tools import AgentToolExecutor, AGENT_TOOLS, ToolResult


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


def test_agent_tools_definitions():
    """Test that all agent tools are properly defined."""
    print("Testing agent tool definitions...")
    
    expected_tools = [
        "get_current_file_content",
        "edit_current_file",
        "open_file",
        "execute_xpath",
        "validate_xml",
        "format_xml",
        "get_open_files",
        "switch_to_tab"
    ]
    
    tool_names = [t["function"]["name"] for t in AGENT_TOOLS]
    
    for expected in expected_tools:
        assert expected in tool_names, f"Missing tool: {expected}"
        print(f"  ✓ {expected}")
    
    print(f"  Total tools defined: {len(AGENT_TOOLS)}\n")


def test_tool_executor_registration():
    """Test tool executor callback registration."""
    print("Testing tool executor registration...")
    
    executor = AgentToolExecutor()
    
    # Register a simple callback
    def mock_callback(**kwargs):
        return "test result"
    
    executor.register_callback("test_tool", mock_callback)
    
    # Test execution
    result = executor.execute_tool("test_tool", {})
    assert result.success, "Tool execution should succeed"
    assert result.result == "test result", "Result should match"
    print("  ✓ Callback registration works\n")


def test_tool_executor_unknown_tool():
    """Test tool executor with unknown tool."""
    print("Testing unknown tool handling...")
    
    executor = AgentToolExecutor()
    
    result = executor.execute_tool("nonexistent_tool", {})
    assert not result.success, "Should fail for unknown tool"
    assert "Unknown tool" in result.error, "Error should mention unknown tool"
    print("  ✓ Unknown tool properly rejected\n")


def test_tool_executor_error_handling():
    """Test tool executor error handling."""
    print("Testing error handling...")
    
    executor = AgentToolExecutor()
    
    def failing_callback(**kwargs):
        raise ValueError("Intentional error")
    
    executor.register_callback("failing_tool", failing_callback)
    
    result = executor.execute_tool("failing_tool", {})
    assert not result.success, "Should fail on exception"
    assert "Tool execution error" in result.error, "Error should mention execution error"
    print("  ✓ Errors properly caught and reported\n")


def test_tool_schema_structure():
    """Test that tool schemas are properly structured for OpenAI API."""
    print("Testing tool schema structure...")
    
    for tool in AGENT_TOOLS:
        assert "type" in tool, "Tool must have type"
        assert tool["type"] == "function", "Tool type must be 'function'"
        assert "function" in tool, "Tool must have function definition"
        
        func = tool["function"]
        assert "name" in func, "Function must have name"
        assert "description" in func, "Function must have description"
        assert "parameters" in func, "Function must have parameters"
        
        params = func["parameters"]
        assert "type" in params, "Parameters must have type"
        assert params["type"] == "object", "Parameters type must be 'object'"
        assert "properties" in params, "Parameters must have properties"
        assert "required" in params, "Parameters must have required list"
        
        print(f"  ✓ {func['name']}: schema valid")
    
    print()


def test_mock_tool_integration():
    """Test integration of tools with mock data."""
    print("Testing mock tool integration...")
    
    executor = AgentToolExecutor()
    
    # Simulate the tools that would be registered by AI assistant
    stored_content = {"value": xml_content}
    
    def get_content():
        return stored_content["value"]
    
    def set_content(new_content):
        stored_content["value"] = new_content
        return "Content updated"
    
    executor.register_callback("get_current_file_content", get_content)
    executor.register_callback("edit_current_file", lambda new_content: set_content(new_content))
    
    # Test get content
    result = executor.execute_tool("get_current_file_content", {})
    assert result.success, "Get content should succeed"
    assert "bookstore" in result.result, "Should return XML content"
    print("  ✓ get_current_file_content works")
    
    # Test edit content
    new_content = "<root>new content</root>"
    result = executor.execute_tool("edit_current_file", {"new_content": new_content})
    assert result.success, "Edit should succeed"
    print("  ✓ edit_current_file works")
    
    # Verify content was updated
    result = executor.execute_tool("get_current_file_content", {})
    assert "new content" in result.result, "Content should be updated"
    print("  ✓ Content properly updated\n")


if __name__ == "__main__":
    print("=" * 60)
    print("AI Agent Tools - Functionality Tests")
    print("=" * 60)
    print()
    
    try:
        test_agent_tools_definitions()
        test_tool_executor_registration()
        test_tool_executor_unknown_tool()
        test_tool_executor_error_handling()
        test_tool_schema_structure()
        test_mock_tool_integration()
        
        print("=" * 60)
        print("All AI agent tools tests passed! ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
