"""
AI Assistant panel for the XML Editor.
Provides an AI-powered assistant to help with XML editing tasks.
"""

import html
import re
from collections import OrderedDict
from lxml import etree
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QComboBox, QScrollArea, QFrame, QApplication, QTextBrowser
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QEvent
from PyQt6.QtGui import QFont, QKeyEvent

from xmleditor.ai_settings_dialog import AISettingsManager, AISettingsDialog
from xmleditor.ai_agent_tools import AgentToolExecutor, AIAgentWorkerThread

# Try to import mermaid-py for diagram rendering
try:
    from mermaid import Mermaid
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False


class MermaidRenderer:
    """Renders mermaid diagram code to SVG images."""
    
    # LRU cache for rendered diagrams with size limit
    _cache = OrderedDict()
    _max_cache_size = 50  # Maximum number of cached diagrams
    
    # Allowed SVG elements for sanitization (whitelist approach)
    _ALLOWED_SVG_ELEMENTS = frozenset([
        'svg', 'g', 'path', 'rect', 'circle', 'ellipse', 'line', 'polyline',
        'polygon', 'text', 'tspan', 'textpath', 'defs', 'use', 'symbol',
        'clippath', 'mask', 'pattern', 'lineargradient', 'radialgradient',
        'stop', 'marker', 'title', 'desc', 'style', 'foreignobject', 'image'
    ])
    
    # Allowed SVG attributes (whitelist approach)
    _ALLOWED_SVG_ATTRS = frozenset([
        'id', 'class', 'style', 'width', 'height', 'viewbox', 'xmlns',
        'xmlns:xlink', 'x', 'y', 'x1', 'y1', 'x2', 'y2', 'cx', 'cy', 'r',
        'rx', 'ry', 'points', 'd', 'fill', 'stroke', 'stroke-width',
        'stroke-dasharray', 'stroke-dashoffset', 'stroke-linecap',
        'stroke-linejoin', 'opacity', 'fill-opacity', 'stroke-opacity',
        'transform', 'font-family', 'font-size', 'font-weight', 'font-style',
        'text-anchor', 'dominant-baseline', 'alignment-baseline', 'dy', 'dx',
        'xlink:href', 'href', 'clip-path', 'mask', 'marker-start', 'marker-mid',
        'marker-end', 'gradientunits', 'gradienttransform', 'spreadmethod',
        'offset', 'stop-color', 'stop-opacity', 'patternunits', 'patterntransform',
        'role', 'aria-roledescription', 'aria-label', 'aria-hidden',
        'preserveaspectratio', 'overflow', 'visibility', 'display'
    ])
    
    @classmethod
    def is_available(cls):
        """Check if mermaid rendering is available."""
        return MERMAID_AVAILABLE
    
    @classmethod
    def _sanitize_svg(cls, svg_content):
        """
        Sanitize SVG content to prevent XSS attacks.
        Removes potentially dangerous elements and attributes.
        
        Args:
            svg_content: Raw SVG string
            
        Returns:
            Sanitized SVG string
        """
        try:
            # Parse the SVG
            parser = etree.XMLParser(remove_comments=True, resolve_entities=False)
            root = etree.fromstring(svg_content.encode('utf-8'), parser)
            
            # Recursively sanitize elements
            cls._sanitize_element(root)
            
            # Return sanitized SVG
            return etree.tostring(root, encoding='unicode')
        except Exception:
            # If parsing fails, return empty SVG to be safe
            return '<svg xmlns="http://www.w3.org/2000/svg"></svg>'
    
    @classmethod
    def _sanitize_element(cls, element):
        """Recursively sanitize an SVG element and its children."""
        # Get local name without namespace
        local_name = element.tag.split('}')[-1].lower() if '}' in element.tag else element.tag.lower()
        
        # Remove disallowed elements
        children_to_remove = []
        for child in element:
            child_local_name = child.tag.split('}')[-1].lower() if '}' in child.tag else child.tag.lower()
            if child_local_name not in cls._ALLOWED_SVG_ELEMENTS:
                children_to_remove.append(child)
            else:
                cls._sanitize_element(child)
        
        for child in children_to_remove:
            element.remove(child)
        
        # Remove disallowed attributes and dangerous patterns
        attrs_to_remove = []
        for attr in element.attrib:
            attr_local = attr.split('}')[-1].lower() if '}' in attr else attr.lower()
            value = element.attrib[attr].lower()
            
            # Remove if not in whitelist
            if attr_local not in cls._ALLOWED_SVG_ATTRS:
                attrs_to_remove.append(attr)
            # Remove javascript: URLs and event handlers
            elif 'javascript:' in value or attr_local.startswith('on'):
                attrs_to_remove.append(attr)
        
        for attr in attrs_to_remove:
            del element.attrib[attr]
    
    @classmethod
    def render_to_svg(cls, mermaid_code):
        """
        Render mermaid code to SVG string.
        
        Args:
            mermaid_code: The mermaid diagram code to render
            
        Returns:
            tuple: (success: bool, result: str) where result is SVG content on success
                   or error message on failure
        """
        if not MERMAID_AVAILABLE:
            return False, "mermaid-py is not installed"
        
        # Check cache first (LRU: move to end if found)
        cache_key = mermaid_code.strip()
        if cache_key in cls._cache:
            cls._cache.move_to_end(cache_key)
            return True, cls._cache[cache_key]
        
        try:
            diagram = Mermaid(mermaid_code)
            response = diagram.svg_response
            
            if response.status_code == 200:
                svg_content = response.text
                # Sanitize SVG to prevent XSS
                sanitized_svg = cls._sanitize_svg(svg_content)
                
                # Add to cache with LRU eviction
                cls._cache[cache_key] = sanitized_svg
                if len(cls._cache) > cls._max_cache_size:
                    cls._cache.popitem(last=False)  # Remove oldest
                
                return True, sanitized_svg
            else:
                return False, f"Failed to render diagram (HTTP {response.status_code})"
        except Exception as e:
            return False, f"Error rendering mermaid diagram: {str(e)}"
    
    @classmethod
    def clear_cache(cls):
        """Clear the diagram cache."""
        cls._cache.clear()


class ChatInputTextEdit(QTextEdit):
    """Custom QTextEdit that handles Enter key for sending messages."""
    
    send_message = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enter_sends = True  # Default: Enter sends, Shift+Enter for newline
    
    def set_enter_sends(self, enabled):
        """Set whether Enter key sends the message."""
        self.enter_sends = enabled
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.enter_sends:
                # Enter sends, Shift+Enter adds newline
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    super().keyPressEvent(event)
                else:
                    self.send_message.emit()
            else:
                # Shift+Enter sends, Enter adds newline
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.send_message.emit()
                else:
                    super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)


class MarkdownRenderer:
    """Renders markdown text to HTML with support for code blocks and mermaid diagrams."""
    
    # CSS styles for markdown rendering
    STYLES = """
    <style>
        .ai-message { color: #333333; margin: 5px 0; background-color: #f5f5f5; padding: 8px; border-radius: 5px; }
        .user-message { color: #0066cc; margin: 5px 0; }
        .code-block { background-color: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 4px; 
                      font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; overflow-x: auto; 
                      white-space: pre-wrap; word-wrap: break-word; }
        .code-block-xml { background-color: #1e3a5f; }
        .code-block-mermaid { background-color: #f0f4f8; color: #333; border: 1px solid #ccd; }
        .inline-code { background-color: #e8e8e8; padding: 2px 5px; border-radius: 3px; 
                       font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; }
        .mermaid-container { background-color: #ffffff; padding: 10px; border-radius: 4px; 
                             border: 1px solid #ddd; margin: 5px 0; }
        .mermaid-placeholder { color: #666; font-style: italic; padding: 10px; 
                               background-color: #f9f9f9; border-radius: 4px; }
        h1, h2, h3, h4 { margin: 10px 0 5px 0; }
        ul, ol { margin: 5px 0; padding-left: 20px; }
        li { margin: 2px 0; }
        blockquote { border-left: 3px solid #ccc; margin: 5px 0; padding-left: 10px; color: #666; }
        strong { font-weight: bold; }
        em { font-style: italic; }
    </style>
    """
    
    @classmethod
    def render(cls, text, is_user=False):
        """Render markdown text to HTML."""
        if is_user:
            escaped = html.escape(text)
            return f'<p class="user-message"><b>You:</b> {escaped}</p>'
        
        # Process the text
        result = cls._process_markdown(text)
        return f'<div class="ai-message"><b>🤖 AI:</b><br>{result}</div>'
    
    @classmethod
    def _process_markdown(cls, text):
        """Process markdown syntax and return HTML."""
        # First, extract and protect code blocks
        code_blocks = []
        
        def save_code_block(match):
            language = match.group(1) or ''
            code = match.group(2)
            index = len(code_blocks)
            code_blocks.append((language.lower(), code))
            return f'%%CODEBLOCK_{index}%%'
        
        # Match fenced code blocks with optional language
        text = re.sub(r'```(\w*)\n?(.*?)```', save_code_block, text, flags=re.DOTALL)
        
        # Extract and protect inline code before HTML escaping
        inline_codes = []
        
        def save_inline_code(match):
            code = match.group(1)
            index = len(inline_codes)
            inline_codes.append(code)
            return f'%%INLINECODE_{index}%%'
        
        text = re.sub(r'`([^`]+)`', save_inline_code, text)
        
        # Process blockquotes BEFORE HTML escaping (while > is still >)
        text = re.sub(r'^> (.+)$', r'%%BLOCKQUOTE_START%%\1%%BLOCKQUOTE_END%%', text, flags=re.MULTILINE)
        
        # Escape HTML in remaining text
        text = html.escape(text)
        
        # Restore blockquotes
        text = text.replace('%%BLOCKQUOTE_START%%', '<blockquote>')
        text = text.replace('%%BLOCKQUOTE_END%%', '</blockquote>')
        
        # Restore inline code with proper escaping
        for i, code in enumerate(inline_codes):
            escaped_code = html.escape(code)
            text = text.replace(f'%%INLINECODE_{i}%%', f'<span class="inline-code">{escaped_code}</span>')
        
        # Process headers
        text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # Process bold and italic
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        
        # Process unordered lists (• and - and *)
        text = re.sub(r'^[\s]*[•\-\*] (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        
        # Wrap consecutive <li> items in <ul>
        text = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\1</ul>', text)
        
        # Process numbered lists - wrap in <ol>
        # First mark numbered list items
        text = re.sub(r'^[\s]*(\d+)\. (.+)$', r'<oli>\2</oli>', text, flags=re.MULTILINE)
        # Wrap consecutive numbered items in <ol>
        text = re.sub(r'((?:<oli>.*?</oli>\n?)+)', r'<ol>\1</ol>', text)
        # Convert <oli> to <li>
        text = text.replace('<oli>', '<li>').replace('</oli>', '</li>')
        
        # Convert newlines to <br> (but not inside block elements)
        text = text.replace('\n', '<br>\n')
        
        # Clean up excessive <br> tags around block elements
        text = re.sub(r'<br>\n*(</?(?:ul|ol|li|h[1-4]|blockquote|div|p)>)', r'\1', text)
        text = re.sub(r'(</(?:ul|ol|h[1-4]|blockquote|div|p)>)\n*<br>', r'\1', text)
        
        # Restore code blocks with proper rendering
        for i, (language, code) in enumerate(code_blocks):
            rendered_block = cls._render_code_block(language, code)
            text = text.replace(f'%%CODEBLOCK_{i}%%', rendered_block)
        
        return text
    
    @classmethod
    def _render_code_block(cls, language, code):
        """Render a code block with syntax highlighting indication."""
        escaped_code = html.escape(code.strip())
        
        if language == 'mermaid':
            # Mermaid diagram - try to render as SVG
            if MermaidRenderer.is_available():
                success, result = MermaidRenderer.render_to_svg(code.strip())
                if success:
                    # Successfully rendered to SVG - display the diagram
                    return (
                        f'<div class="mermaid-container">'
                        f'<div style="color: #666; font-size: 10px; margin-bottom: 5px;">📊 Mermaid Diagram:</div>'
                        f'{result}'
                        f'</div>'
                    )
                else:
                    # Rendering failed - show error and code
                    return (
                        f'<div class="mermaid-container">'
                        f'<div style="color: #cc6600; font-size: 10px; margin-bottom: 5px;">⚠️ Mermaid Diagram (render failed: {html.escape(result)}):</div>'
                        f'<pre class="code-block code-block-mermaid">{escaped_code}</pre>'
                        f'</div>'
                    )
            else:
                # mermaid-py not available - show code with note
                return (
                    f'<div class="mermaid-container">'
                    f'<div style="color: #666; font-size: 10px; margin-bottom: 5px;">📊 Mermaid Diagram (install mermaid-py to render):</div>'
                    f'<pre class="code-block code-block-mermaid">{escaped_code}</pre>'
                    f'</div>'
                )
        elif language in ('xml', 'html', 'xsd', 'xslt', 'dtd'):
            # XML-family languages with special styling
            return f'<pre class="code-block code-block-xml">{escaped_code}</pre>'
        else:
            # Generic code block
            lang_label = f'<div style="color: #888; font-size: 10px; margin-bottom: 3px;">{language}</div>' if language else ''
            return f'{lang_label}<pre class="code-block">{escaped_code}</pre>'
    
    @classmethod
    def get_styles(cls):
        """Return the CSS styles for the chat display."""
        return cls.STYLES


class AIAssistantPanel(QWidget):
    """AI Assistant panel for XML-related help and suggestions."""
    
    # Signal emitted when AI suggests XML content to apply
    apply_suggestion = pyqtSignal(str)
    
    # Signals for agentic file operations (connected by MainWindow)
    request_open_file = pyqtSignal(str)  # Request to open a file by path
    request_switch_tab = pyqtSignal(str)  # Request to switch to a tab
    
    # Constants for AI context limits
    MAX_XML_CONTEXT_LENGTH = 4000
    MAX_CONVERSATION_HISTORY = 6
    
    # System prompt for the AI with agentic capabilities
    SYSTEM_PROMPT = """You are an expert XML assistant integrated into an XML editor application. 
You have special tools that allow you to interact with the editor directly:

**Available Tools:**
- `get_current_file_content`: Get the content of the currently open XML file
- `edit_current_file`: Replace the content of the current file with new XML content
- `open_file`: Open a file by its path in a new tab
- `execute_xpath`: Execute XPath queries on the current document
- `validate_xml`: Validate XML for well-formedness or against a schema
- `format_xml`: Format/prettify the current XML document
- `get_open_files`: List all currently open files/tabs
- `switch_to_tab`: Switch to a specific tab by index or filename

**Guidelines:**
- When the user asks you to edit the file, use the `edit_current_file` tool to make changes directly
- Use `execute_xpath` to analyze the document structure before making complex edits
- Always validate changes after editing to ensure the XML is still well-formed
- When explaining errors, use the actual document content from `get_current_file_content`
- Be proactive in using tools to help the user accomplish their task

You can chain multiple tool calls together to complete complex tasks. For example:
1. Get the current content
2. Analyze it with XPath
3. Make edits
4. Validate the result

Be concise but helpful. Format XML examples clearly when showing them to the user."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.xml_content = ""
        self.settings_manager = AISettingsManager()
        self.worker_thread = None
        self.conversation_history = []
        
        # Initialize the tool executor
        self.tool_executor = AgentToolExecutor()
        self._register_local_tools()
        
        # Callbacks that will be set by MainWindow
        self._get_current_content_callback = None
        self._set_current_content_callback = None
        self._get_open_files_callback = None
        self._open_file_callback = None
        self._switch_tab_callback = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header with title and settings button
        header_layout = QHBoxLayout()
        title_label = QLabel("🤖 AI Assistant")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Settings button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setToolTip("Configure AI settings")
        self.settings_btn.setMaximumWidth(30)
        self.settings_btn.clicked.connect(self.show_settings_dialog)
        header_layout.addWidget(self.settings_btn)
        
        layout.addLayout(header_layout)
        
        # Quick action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(3)
        
        self.explain_btn = QPushButton("📖 Explain")
        self.explain_btn.setToolTip("Explain the current XML structure")
        self.explain_btn.clicked.connect(lambda: self.quick_action("explain"))
        actions_layout.addWidget(self.explain_btn)
        
        self.fix_btn = QPushButton("🔧 Fix Errors")
        self.fix_btn.setToolTip("Suggest fixes for XML errors")
        self.fix_btn.clicked.connect(lambda: self.quick_action("fix"))
        actions_layout.addWidget(self.fix_btn)
        
        self.optimize_btn = QPushButton("✨ Optimize")
        self.optimize_btn.setToolTip("Suggest optimizations for the XML")
        self.optimize_btn.clicked.connect(lambda: self.quick_action("optimize"))
        actions_layout.addWidget(self.optimize_btn)
        
        self.generate_btn = QPushButton("📝 Generate")
        self.generate_btn.setToolTip("Generate XML based on description")
        self.generate_btn.clicked.connect(lambda: self.quick_action("generate"))
        actions_layout.addWidget(self.generate_btn)
        
        layout.addLayout(actions_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Chat history display area - use QTextBrowser for better HTML rendering
        self.chat_display = QTextBrowser()
        self.chat_display.setReadOnly(True)
        self.chat_display.setOpenExternalLinks(False)
        self.chat_display.setPlaceholderText(
            "AI Assistant is ready to help!\n\n"
            "• Click a quick action button above\n"
            "• Or type your question below\n\n"
            "Examples:\n"
            "• 'Explain this XML structure'\n"
            "• 'Add a new child element called <item>'\n"
            "• 'Convert to a different namespace'"
        )
        # Initialize with styles
        self.chat_html_content = MarkdownRenderer.get_styles()
        layout.addWidget(self.chat_display, 1)
        
        # User input area
        input_layout = QHBoxLayout()
        
        self.user_input = ChatInputTextEdit()
        self.user_input.setPlaceholderText("Ask AI about your XML... (Enter to send, Shift+Enter for newline)")
        self.user_input.setMaximumHeight(60)
        self.user_input.send_message.connect(self.send_message)
        # Load enter key preference
        enter_sends = self.settings_manager.load_settings().get("enter_sends_message", True)
        self.user_input.set_enter_sends(enter_sends)
        input_layout.addWidget(self.user_input)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setMinimumWidth(60)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # Status/info label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.status_label)
        
        # Initialize chat with welcome message
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """Show the welcome message based on configuration status."""
        if self.settings_manager.is_configured():
            self.add_ai_message(
                "👋 Hello! I'm your AI assistant for XML editing.\n\n"
                "I can help you:\n"
                "• Understand XML structure\n"
                "• Fix validation errors\n"
                "• Generate XML content\n"
                "• Optimize your documents\n\n"
                "Load an XML document and ask me anything!"
            )
        else:
            self.add_ai_message(
                "👋 Hello! I'm your AI assistant for XML editing.\n\n"
                "⚠️ API not configured yet!\n\n"
                "Click the ⚙️ button above to configure:\n"
                "• API endpoint (OpenRouter, OpenAI, etc.)\n"
                "• Your API key\n"
                "• Model selection\n\n"
                "Once configured, I can provide AI-powered assistance!"
            )
    
    def show_settings_dialog(self):
        """Open the AI settings dialog."""
        dialog = AISettingsDialog(self)
        if dialog.exec():
            # Settings were saved, reload them
            self.settings_manager.reload_settings()
            # Update enter key behavior
            enter_sends = self.settings_manager.load_settings().get("enter_sends_message", True)
            self.user_input.set_enter_sends(enter_sends)
            # Update placeholder text
            if enter_sends:
                self.user_input.setPlaceholderText("Ask AI about your XML... (Enter to send, Shift+Enter for newline)")
            else:
                self.user_input.setPlaceholderText("Ask AI about your XML... (Shift+Enter to send, Enter for newline)")
            self.add_ai_message("✅ Settings saved! AI assistant is now configured.")
    
    def _register_local_tools(self):
        """Register local tool implementations with the tool executor."""
        self.tool_executor.register_callback("get_current_file_content", self._tool_get_current_content)
        self.tool_executor.register_callback("edit_current_file", self._tool_edit_current_file)
        self.tool_executor.register_callback("open_file", self._tool_open_file)
        self.tool_executor.register_callback("execute_xpath", self._tool_execute_xpath)
        self.tool_executor.register_callback("validate_xml", self._tool_validate_xml)
        self.tool_executor.register_callback("format_xml", self._tool_format_xml)
        self.tool_executor.register_callback("get_open_files", self._tool_get_open_files)
        self.tool_executor.register_callback("switch_to_tab", self._tool_switch_to_tab)
    
    def set_editor_callbacks(self, get_content, set_content, get_open_files, open_file, switch_tab):
        """
        Set callbacks for editor operations.
        These are called by the tool executor when the AI uses tools.
        
        Args:
            get_content: Callable that returns current editor content
            set_content: Callable that sets current editor content
            get_open_files: Callable that returns list of open files
            open_file: Callable that opens a file by path
            switch_tab: Callable that switches to a tab
        """
        self._get_current_content_callback = get_content
        self._set_current_content_callback = set_content
        self._get_open_files_callback = get_open_files
        self._open_file_callback = open_file
        self._switch_tab_callback = switch_tab
    
    def _tool_get_current_content(self) -> str:
        """Tool: Get the current file content."""
        if self._get_current_content_callback:
            content = self._get_current_content_callback()
            if content:
                return content
            return "No file is currently open."
        # Fallback to cached content
        return self.xml_content if self.xml_content else "No file is currently open."
    
    def _tool_edit_current_file(self, new_content: str) -> str:
        """Tool: Edit the current file with new content."""
        if not self._set_current_content_callback:
            return "Error: Editor connection not available."
        
        try:
            self._set_current_content_callback(new_content)
            # Update our cached content
            self.xml_content = new_content
            return "File content updated successfully."
        except Exception as e:
            return f"Error updating file: {str(e)}"
    
    def _tool_open_file(self, file_path: str) -> str:
        """Tool: Open a file by path."""
        if not self._open_file_callback:
            return "Error: Editor connection not available."
        
        try:
            self._open_file_callback(file_path)
            return f"Opened file: {file_path}"
        except Exception as e:
            return f"Error opening file: {str(e)}"
    
    def _tool_execute_xpath(self, xpath_expression: str, context_xpath: str = "") -> str:
        """Tool: Execute an XPath query."""
        from xmleditor.xml_utils import XMLUtilities
        
        content = self._tool_get_current_content()
        if content.startswith("No file") or content.startswith("Error"):
            return content
        
        try:
            results = XMLUtilities.xpath_query(content, xpath_expression, context_xpath)
            if not results:
                return "XPath query returned no results."
            
            # Format results
            if len(results) == 1:
                return f"Result:\n{results[0]}"
            else:
                formatted = f"Found {len(results)} results:\n"
                for i, result in enumerate(results[:20], 1):  # Limit to 20 results
                    formatted += f"\n{i}. {result}"
                if len(results) > 20:
                    formatted += f"\n... and {len(results) - 20} more results"
                return formatted
        except Exception as e:
            return f"XPath error: {str(e)}"
    
    def _tool_validate_xml(self, schema_content: str = "") -> str:
        """Tool: Validate XML content."""
        from xmleditor.xml_utils import XMLUtilities
        
        content = self._tool_get_current_content()
        if content.startswith("No file") or content.startswith("Error"):
            return content
        
        try:
            if schema_content:
                is_valid, message = XMLUtilities.validate_with_xsd(content, schema_content)
            else:
                is_valid, message = XMLUtilities.validate_xml(content)
            
            return message
        except Exception as e:
            return f"Validation error: {str(e)}"
    
    def _tool_format_xml(self) -> str:
        """Tool: Format the current XML document."""
        from xmleditor.xml_utils import XMLUtilities
        
        content = self._tool_get_current_content()
        if content.startswith("No file") or content.startswith("Error"):
            return content
        
        try:
            formatted = XMLUtilities.format_xml(content)
            # Apply the formatted content
            result = self._tool_edit_current_file(formatted)
            if "successfully" in result:
                return "XML formatted successfully."
            return result
        except Exception as e:
            return f"Format error: {str(e)}"
    
    def _tool_get_open_files(self) -> str:
        """Tool: Get list of open files."""
        if not self._get_open_files_callback:
            return "Error: Editor connection not available."
        
        try:
            files = self._get_open_files_callback()
            if not files:
                return "No files are currently open."
            
            result = "Open files:\n"
            for i, file_info in enumerate(files):
                modified = " *" if file_info.get("is_modified", False) else ""
                current = " (current)" if file_info.get("is_current", False) else ""
                result += f"{i}. {file_info.get('name', 'Untitled')}{modified}{current}\n"
            return result
        except Exception as e:
            return f"Error getting open files: {str(e)}"
    
    def _tool_switch_to_tab(self, tab_identifier: str) -> str:
        """Tool: Switch to a specific tab."""
        if not self._switch_tab_callback:
            return "Error: Editor connection not available."
        
        try:
            self._switch_tab_callback(tab_identifier)
            return f"Switched to tab: {tab_identifier}"
        except Exception as e:
            return f"Error switching tab: {str(e)}"
    
    @pyqtSlot(str)
    def on_tool_call_started(self, tool_name: str):
        """Handle when a tool call starts."""
        self.status_label.setText(f"🔧 Using tool: {tool_name}...")
    
    @pyqtSlot(str, str)
    def on_tool_call_completed(self, tool_name: str, result: str):
        """Handle when a tool call completes."""
        # Show a brief status of tool completion
        status = "✓" if "Error" not in result else "✗"
        self.status_label.setText(f"🔧 {tool_name}: {status}")
    
    def call_ai_api(self, user_message, context_info=""):
        """Make an API call to the AI service with agentic capabilities."""
        if not self.settings_manager.is_configured():
            self.add_ai_message(
                "⚠️ API not configured!\n\n"
                "Please click the ⚙️ button to configure your API settings."
            )
            return
        
        # Build the messages for the API
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        
        # Add context info if provided (e.g., for quick actions)
        if context_info:
            messages.append({"role": "system", "content": context_info})
        
        # Add conversation history (limited to keep context manageable)
        messages.extend(self.conversation_history[-self.MAX_CONVERSATION_HISTORY:])
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        # Store in conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Disable input while processing
        self.set_input_enabled(False)
        self.status_label.setText("⏳ Waiting for AI response...")
        
        # Start the agentic worker thread with tool support
        self.worker_thread = AIAgentWorkerThread(
            self.settings_manager.get_api_url(),
            self.settings_manager.get_api_key(),
            self.settings_manager.get_model(),
            messages,
            self.tool_executor
        )
        self.worker_thread.response_ready.connect(self.on_ai_response)
        self.worker_thread.error_occurred.connect(self.on_ai_error)
        self.worker_thread.tool_call_started.connect(self.on_tool_call_started)
        self.worker_thread.tool_call_completed.connect(self.on_tool_call_completed)
        self.worker_thread.start()
    
    @pyqtSlot(str)
    def on_ai_response(self, response):
        """Handle successful AI response."""
        self.set_input_enabled(True)
        self.update_status_label()
        
        # Store in conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        self.add_ai_message(response)
    
    @pyqtSlot(str)
    def on_ai_error(self, error_message):
        """Handle AI API error."""
        self.set_input_enabled(True)
        self.update_status_label()
        self.add_ai_message(f"❌ {error_message}")
    
    def set_input_enabled(self, enabled):
        """Enable or disable input controls."""
        self.user_input.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)
        self.explain_btn.setEnabled(enabled)
        self.fix_btn.setEnabled(enabled)
        self.optimize_btn.setEnabled(enabled)
        self.generate_btn.setEnabled(enabled)
    
    def update_status_label(self):
        """Update status label with current context info."""
        if self.xml_content.strip():
            lines = self.xml_content.count('\n') + 1
            chars = len(self.xml_content)
            self.status_label.setText(f"Context: {lines} lines, {chars} characters")
        else:
            self.status_label.setText("No XML content loaded")
    
    def set_xml_content(self, content):
        """Set the current XML content for context."""
        self.xml_content = content
        if content.strip():
            lines = content.count('\n') + 1
            chars = len(content)
            self.status_label.setText(f"Context: {lines} lines, {chars} characters")
        else:
            self.status_label.setText("No XML content loaded")
    
    def quick_action(self, action_type):
        """Handle quick action button clicks."""
        # Generate action works differently - it pre-fills the input
        if action_type == "generate":
            self.user_input.setPlaceholderText("Describe the XML you want to generate...")
            self.user_input.setFocus()
            return
        
        if not self.xml_content.strip():
            self.add_ai_message(
                "⚠️ No XML content found. Please load or create an XML document first."
            )
            return
        
        # Use AI API if configured, otherwise use local analysis
        if self.settings_manager.is_configured():
            if action_type == "explain":
                self.add_user_message("Explain this XML structure")
                self.call_ai_api(
                    "Please analyze and explain the structure of this XML document. "
                    "Include information about the root element, child elements, attributes, "
                    "namespaces if any, and the overall purpose of the document."
                )
            elif action_type == "fix":
                self.add_user_message("Check for errors and suggest fixes")
                self.call_ai_api(
                    "Please check this XML document for any errors, issues, or problems. "
                    "If there are errors, explain what's wrong and suggest how to fix them. "
                    "If the document is well-formed, confirm that and mention any potential improvements."
                )
            elif action_type == "optimize":
                self.add_user_message("Suggest optimizations")
                self.call_ai_api(
                    "Please analyze this XML document and suggest optimizations or improvements. "
                    "Consider structure, readability, efficiency, and best practices."
                )
        else:
            # Fallback to local analysis
            if action_type == "explain":
                self.add_user_message("Explain this XML structure")
                self.explain_xml_local()
            elif action_type == "fix":
                self.add_user_message("Check for errors and suggest fixes")
                self.fix_errors_local()
            elif action_type == "optimize":
                self.add_user_message("Suggest optimizations")
                self.suggest_optimizations_local()
    
    def send_message(self):
        """Send user message and get AI response."""
        message = self.user_input.toPlainText().strip()
        if not message:
            return
        
        self.add_user_message(message)
        self.user_input.clear()
        
        # Process the message and generate response
        self.process_user_message(message)
    
    def process_user_message(self, message):
        """Process user message and generate AI response."""
        # Use AI API if configured
        if self.settings_manager.is_configured():
            self.call_ai_api(message)
        else:
            # Fallback to local processing
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['explain', 'what is', 'describe', 'tell me about']):
                self.explain_xml_local()
            elif any(word in message_lower for word in ['fix', 'error', 'wrong', 'problem', 'issue']):
                self.fix_errors_local()
            elif any(word in message_lower for word in ['optimize', 'improve', 'better', 'simplify']):
                self.suggest_optimizations_local()
            elif any(word in message_lower for word in ['generate', 'create', 'add', 'make', 'new']):
                self.generate_content_help(message)
            elif any(word in message_lower for word in ['validate', 'check', 'valid']):
                self.check_validation()
            elif any(word in message_lower for word in ['help', 'what can']):
                self.show_help()
            else:
                self.general_response(message)
    
    def explain_xml_local(self):
        """Explain the current XML structure."""
        if not self.xml_content.strip():
            self.add_ai_message("⚠️ No XML content to explain. Please load an XML document first.")
            return
        
        try:
            root = etree.fromstring(self.xml_content.encode('utf-8'))
            
            # Gather structure information
            root_tag = root.tag
            namespaces = root.nsmap
            child_tags = set(child.tag for child in root)
            total_elements = len(root.xpath('//*'))
            total_attrs = sum(len(elem.attrib) for elem in root.xpath('//*'))
            
            ns_info = ""
            if namespaces:
                ns_list = [f"  • {prefix or 'default'}: {uri}" for prefix, uri in namespaces.items()]
                ns_info = "\n\n📍 Namespaces:\n" + "\n".join(ns_list)
            
            children_info = ""
            if child_tags:
                children_info = "\n\n👶 Direct children of root:\n" + "\n".join(f"  • <{tag}>" for tag in child_tags)
            
            explanation = (
                f"📄 **XML Structure Analysis**\n\n"
                f"🏷️ Root element: <{root_tag}>\n"
                f"📊 Total elements: {total_elements}\n"
                f"🔧 Total attributes: {total_attrs}"
                f"{ns_info}"
                f"{children_info}\n\n"
                f"The document appears to be well-formed XML."
            )
            
            self.add_ai_message(explanation)
            
        except etree.XMLSyntaxError as e:
            self.add_ai_message(
                f"⚠️ XML Parsing Error:\n{str(e)}\n\n"
                "The document has syntax errors. Click 'Fix Errors' for suggestions."
            )
        except Exception as e:
            self.add_ai_message(f"❌ Error analyzing XML: {str(e)}")
    
    def fix_errors_local(self):
        """Check for errors and suggest fixes (local analysis)."""
        if not self.xml_content.strip():
            self.add_ai_message("⚠️ No XML content to check. Please load an XML document first.")
            return
        
        try:
            etree.fromstring(self.xml_content.encode('utf-8'))
            self.add_ai_message(
                "✅ **No Errors Found**\n\n"
                "The XML document is well-formed!\n\n"
                "For schema validation, use the Validation Panel (Ctrl+Shift+P)."
            )
        except etree.XMLSyntaxError as e:
            error_msg = str(e)
            line_match = None
            
            # Try to extract line number
            if "line" in error_msg.lower():
                line_match = re.search(r'line (\d+)', error_msg)
            
            suggestions = self.get_error_suggestions(error_msg)
            
            response = f"❌ **XML Error Found**\n\n"
            response += f"Error: {error_msg}\n\n"
            
            if line_match:
                response += f"📍 Location: Line {line_match.group(1)}\n\n"
            
            response += "💡 **Suggestions:**\n"
            for suggestion in suggestions:
                response += f"  • {suggestion}\n"
            
            self.add_ai_message(response)
    
    def get_error_suggestions(self, error_msg):
        """Get suggestions based on error message."""
        suggestions = []
        error_lower = error_msg.lower()
        
        if "opening and ending tag mismatch" in error_lower:
            suggestions.append("Check that all opening tags have matching closing tags")
            suggestions.append("Verify tag names are spelled consistently (XML is case-sensitive)")
            suggestions.append("Use Format XML (Ctrl+Shift+F) to see the structure clearly")
        elif "not well-formed" in error_lower or "invalid token" in error_lower:
            suggestions.append("Check for special characters that need escaping: & < > \" '")
            suggestions.append("Use &amp; &lt; &gt; &quot; &apos; for special characters")
            suggestions.append("Ensure attribute values are in quotes")
        elif "encoding" in error_lower:
            suggestions.append("Check that the declared encoding matches the file encoding")
            suggestions.append("Try removing the encoding declaration or use UTF-8")
        elif "namespace" in error_lower:
            suggestions.append("Ensure all namespace prefixes are declared")
            suggestions.append("Check for xmlns declarations in the root element")
        else:
            suggestions.append("Check for unclosed tags or missing quotes")
            suggestions.append("Verify the XML declaration is correct")
            suggestions.append("Ensure there's only one root element")
        
        return suggestions
    
    def suggest_optimizations_local(self):
        """Suggest optimizations for the XML (local analysis)."""
        if not self.xml_content.strip():
            self.add_ai_message("⚠️ No XML content to optimize. Please load an XML document first.")
            return
        
        try:
            root = etree.fromstring(self.xml_content.encode('utf-8'))
            
            suggestions = []
            
            # Check for empty elements that could use self-closing tags
            empty_elements = [elem for elem in root.xpath('//*') if len(elem) == 0 and not elem.text]
            if empty_elements:
                suggestions.append(f"💡 Found {len(empty_elements)} empty elements - consider using self-closing tags")
            
            # Check for excessive nesting
            max_depth = self.get_max_depth(root)
            if max_depth > 10:
                suggestions.append(f"📊 Deep nesting detected (depth: {max_depth}) - consider flattening the structure")
            
            # Check for duplicate attribute values that might benefit from entity references
            all_attrs = [attr for elem in root.xpath('//*') for attr in elem.attrib.values()]
            attr_counts = {}
            for attr in all_attrs:
                if len(attr) > 20:
                    attr_counts[attr] = attr_counts.get(attr, 0) + 1
            
            repeated_attrs = [k for k, v in attr_counts.items() if v > 2]
            if repeated_attrs:
                suggestions.append("🔄 Found repeated long attribute values - consider using entity references")
            
            # Check for very long text content
            long_text = [elem for elem in root.xpath('//*') if elem.text and len(elem.text) > 1000]
            if long_text:
                suggestions.append(f"📝 Found {len(long_text)} elements with very long text - consider using CDATA sections")
            
            if suggestions:
                response = "✨ **Optimization Suggestions:**\n\n"
                for suggestion in suggestions:
                    response += f"  {suggestion}\n"
            else:
                response = (
                    "✅ **Document looks good!**\n\n"
                    "No obvious optimizations needed. The XML structure appears clean and efficient."
                )
            
            self.add_ai_message(response)
            
        except Exception as e:
            self.add_ai_message(f"❌ Error analyzing XML for optimizations: {str(e)}")
    
    def get_max_depth(self, element, current_depth=0):
        """Calculate maximum nesting depth."""
        if len(element) == 0:
            return current_depth
        return max(self.get_max_depth(child, current_depth + 1) for child in element)
    
    def generate_content_help(self, message):
        """Help user generate XML content."""
        response = (
            "📝 **XML Generation Help**\n\n"
            "I can help you structure XML. Here are some templates:\n\n"
            "**Simple Element:**\n"
            "```xml\n"
            "<element attribute=\"value\">\n"
            "    content\n"
            "</element>\n"
            "```\n\n"
            "**List Structure:**\n"
            "```xml\n"
            "<items>\n"
            "    <item id=\"1\">First</item>\n"
            "    <item id=\"2\">Second</item>\n"
            "</items>\n"
            "```\n\n"
            "Tell me more specifically what you want to create!"
        )
        self.add_ai_message(response)
    
    def check_validation(self):
        """Guide user to validation."""
        self.add_ai_message(
            "✅ **Validation Guide**\n\n"
            "For full XML validation:\n\n"
            "1. Open Validation Panel: **View → Toggle Validation Panel** (Ctrl+Shift+P)\n"
            "2. Check well-formedness: Click **Well-Formed** button\n"
            "3. For schema validation:\n"
            "   • Load your XSD or DTD file\n"
            "   • Click **Validate XSD** or **Validate DTD**\n\n"
            "You can also use the quick **'Fix Errors'** button above to check for basic errors."
        )
    
    def show_help(self):
        """Show help information."""
        self.add_ai_message(
            "🤖 **AI Assistant Help**\n\n"
            "I can help you with:\n\n"
            "📖 **Explain** - Understand your XML structure\n"
            "🔧 **Fix Errors** - Find and fix XML syntax errors\n"
            "✨ **Optimize** - Get suggestions for improvement\n"
            "📝 **Generate** - Help creating new XML content\n\n"
            "**Tips:**\n"
            "• Load an XML document first\n"
            "• Use quick action buttons or type your question\n"
            "• Ask specific questions for better answers"
        )
    
    def general_response(self, message):
        """Provide a general response."""
        # Truncate and escape user message for safe display
        truncated_msg = message[:50] if len(message) > 50 else message
        self.add_ai_message(
            f"🤔 I received your message about: \"{truncated_msg}...\"\n\n"
            "I'm here to help with XML-related tasks. Try:\n"
            "• 'Explain this XML'\n"
            "• 'Check for errors'\n"
            "• 'How do I add an element?'\n"
            "• 'Help me validate'\n\n"
            "Or use the quick action buttons above!"
        )
    
    def add_user_message(self, message):
        """Add a user message to the chat display."""
        user_html = MarkdownRenderer.render(message, is_user=True)
        self.chat_html_content += user_html
        self.chat_display.setHtml(self.chat_html_content)
        self.scroll_to_bottom()
    
    def add_ai_message(self, message):
        """Add an AI message to the chat display."""
        ai_html = MarkdownRenderer.render(message, is_user=False)
        self.chat_html_content += ai_html
        self.chat_display.setHtml(self.chat_html_content)
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll chat display to bottom."""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_chat(self):
        """Clear the chat history."""
        self.chat_html_content = MarkdownRenderer.get_styles()
        self.chat_display.clear()
        self.add_ai_message(
            "👋 Chat cleared! I'm ready to help with your XML editing tasks."
        )
