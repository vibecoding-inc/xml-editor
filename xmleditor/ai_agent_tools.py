"""
AI Agent Tools for the XML Editor.
Provides function calling tools that allow the AI assistant to interact with the editor.
"""

import json
from typing import Callable, Optional, Dict
from dataclasses import dataclass

from PyQt6.QtCore import QThread, pyqtSignal

# Tool definitions for OpenRouter/OpenAI function calling
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_file_content",
            "description": "Get the content of the currently active/open XML file in the editor",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_current_file",
            "description": "Replace the entire content of the currently active XML file with new content. Use this to make edits to the file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_content": {
                        "type": "string",
                        "description": "The new XML content to replace the current file content with"
                    }
                },
                "required": ["new_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_file",
            "description": "Open a file by its path in the editor. The file will be opened in a new tab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The absolute or relative path to the file to open"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_xpath",
            "description": "Execute an XPath query on the currently open XML document and return the results. Useful for finding or extracting specific elements.",
            "parameters": {
                "type": "object",
                "properties": {
                    "xpath_expression": {
                        "type": "string",
                        "description": "The XPath expression to execute (e.g., '//book/title', '//@id', 'count(//item)')"
                    },
                    "context_xpath": {
                        "type": "string",
                        "description": "Optional XPath to select the context node from which to execute the query"
                    }
                },
                "required": ["xpath_expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_xml",
            "description": "Validate the currently open XML document for well-formedness and optionally against a schema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "schema_content": {
                        "type": "string",
                        "description": "Optional XSD schema content to validate against. If not provided, only well-formedness is checked."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "format_xml",
            "description": "Format and prettify the currently open XML document with proper indentation",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_open_files",
            "description": "Get a list of all currently open files/tabs in the editor",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "switch_to_tab",
            "description": "Switch to a specific tab/file by its index or filename",
            "parameters": {
                "type": "object",
                "properties": {
                    "tab_identifier": {
                        "type": "string",
                        "description": "The tab index (0-based) or filename to switch to"
                    }
                },
                "required": ["tab_identifier"]
            }
        }
    }
]


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    result: str
    error: Optional[str] = None


class AgentToolExecutor:
    """
    Executes AI agent tools by calling registered callbacks.
    This class bridges the AI agent with the main window functionality.
    """
    
    def __init__(self):
        self._callbacks: Dict[str, Callable] = {}
    
    def register_callback(self, tool_name: str, callback: Callable) -> None:
        """Register a callback function for a specific tool."""
        self._callbacks[tool_name] = callback
    
    def execute_tool(self, tool_name: str, arguments: dict) -> ToolResult:
        """
        Execute a tool with the given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Dictionary of arguments for the tool
            
        Returns:
            ToolResult with the execution result
        """
        if tool_name not in self._callbacks:
            return ToolResult(
                success=False,
                result="",
                error=f"Unknown tool: {tool_name}"
            )
        
        try:
            callback = self._callbacks[tool_name]
            result = callback(**arguments)
            return ToolResult(success=True, result=str(result))
        except Exception as e:
            return ToolResult(
                success=False,
                result="",
                error=f"Tool execution error: {str(e)}"
            )


class AIAgentWorkerThread(QThread):
    """
    Worker thread for making AI API calls with function calling support.
    Implements an agentic loop that handles tool calls until completion.
    """
    
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    tool_call_started = pyqtSignal(str)  # Emits tool name when a tool call starts
    tool_call_completed = pyqtSignal(str, str)  # Emits tool name and result
    
    MAX_TOOL_ITERATIONS = 10  # Maximum number of tool call iterations
    
    def __init__(self, api_url: str, api_key: str, model: str, messages: list,
                 tool_executor: AgentToolExecutor):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.messages = messages
        self.tool_executor = tool_executor
        self._openai_client = None
    
    def _get_client(self):
        """Get or create the OpenAI client."""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                
                # Extract base URL from full API URL
                # OpenRouter uses https://openrouter.ai/api/v1/chat/completions
                # We need https://openrouter.ai/api/v1 for the base_url
                base_url = self.api_url
                if base_url.endswith('/chat/completions'):
                    base_url = base_url[:-len('/chat/completions')]
                
                self._openai_client = OpenAI(
                    base_url=base_url,
                    api_key=self.api_key,
                    default_headers={
                        "HTTP-Referer": "https://github.com/profiluefter/xml-editor",
                        "X-Title": "XML Editor AI Assistant"
                    }
                )
            except ImportError:
                raise RuntimeError("openai package is not installed")
        return self._openai_client
    
    def run(self):
        """Execute the agentic API call loop."""
        try:
            client = self._get_client()
            messages = list(self.messages)
            
            iterations = 0
            while iterations < self.MAX_TOOL_ITERATIONS:
                iterations += 1
                
                # Make API call with tools
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=AGENT_TOOLS,
                    tool_choice="auto",
                    max_tokens=2000,
                    temperature=0.7
                )
                
                assistant_message = response.choices[0].message
                
                # Check if the model wants to call tools
                if assistant_message.tool_calls:
                    # Add assistant message to conversation
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    })
                    
                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {}
                        
                        self.tool_call_started.emit(tool_name)
                        
                        # Execute the tool
                        result = self.tool_executor.execute_tool(tool_name, arguments)
                        
                        if result.success:
                            tool_result = result.result
                            self.tool_call_completed.emit(tool_name, "Success")
                        else:
                            tool_result = f"Error: {result.error}"
                            self.tool_call_completed.emit(tool_name, f"Error: {result.error}")
                        
                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })
                else:
                    # No more tool calls, return the final response
                    content = assistant_message.content or "Task completed."
                    self.response_ready.emit(content)
                    return
            
            # Exceeded max iterations
            self.response_ready.emit(
                "I've completed multiple tool operations. Let me know if you need anything else."
            )
            
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                self.error_occurred.emit("Invalid API key. Please check your settings.")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                self.error_occurred.emit("Rate limit exceeded. Please wait and try again.")
            elif "ImportError" in error_msg or "openai" in error_msg.lower():
                self.error_occurred.emit("OpenAI SDK not installed. Please install 'openai' package.")
            else:
                self.error_occurred.emit(f"API Error: {error_msg[:200]}")
