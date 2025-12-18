"""
AI Assistant panel for the XML Editor.
Provides an AI-powered assistant to help with XML editing tasks.
"""

import html
import re
import json
import urllib.request
import urllib.error
from lxml import etree
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QComboBox, QScrollArea, QFrame, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont

from xmleditor.ai_settings_dialog import AISettingsManager, AISettingsDialog


class AIWorkerThread(QThread):
    """Worker thread for making AI API calls without blocking the UI."""
    
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_url, api_key, model, messages):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.messages = messages
    
    def run(self):
        """Execute the API call."""
        try:
            data = json.dumps({
                "model": self.model,
                "messages": self.messages,
                "max_tokens": 2000,
                "temperature": 0.7
            }).encode('utf-8')
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/xml-editor",
                "X-Title": "XML Editor AI Assistant"
            }
            
            req = urllib.request.Request(self.api_url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {})
                    content = message.get('content', 'No response content')
                    self.response_ready.emit(content)
                else:
                    self.error_occurred.emit("Unexpected API response format")
        
        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode('utf-8')
            except Exception:
                pass
            
            if e.code == 401:
                self.error_occurred.emit("Invalid API key. Please check your settings.")
            elif e.code == 429:
                self.error_occurred.emit("Rate limit exceeded. Please wait and try again.")
            else:
                self.error_occurred.emit(f"API Error ({e.code}): {error_body[:100]}")
        
        except urllib.error.URLError as e:
            self.error_occurred.emit(f"Connection error: {str(e.reason)}")
        
        except json.JSONDecodeError:
            self.error_occurred.emit("Failed to parse API response")
        
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")


class AIAssistantPanel(QWidget):
    """AI Assistant panel for XML-related help and suggestions."""
    
    # Signal emitted when AI suggests XML content to apply
    apply_suggestion = pyqtSignal(str)
    
    # Constants for AI context limits
    MAX_XML_CONTEXT_LENGTH = 4000
    MAX_CONVERSATION_HISTORY = 6
    
    # System prompt for the AI
    SYSTEM_PROMPT = """You are an expert XML assistant integrated into an XML editor application. 
Your role is to help users with XML-related tasks including:
- Explaining XML structure and elements
- Finding and fixing XML errors
- Suggesting optimizations and best practices
- Generating XML content based on descriptions
- Answering questions about XML, XSD, DTD, XPath, and XSLT

When providing XML examples, format them clearly. Be concise but helpful.
The user is currently working with an XML document in the editor."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.xml_content = ""
        self.settings_manager = AISettingsManager()
        self.worker_thread = None
        self.conversation_history = []
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
        
        # Chat history display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText(
            "AI Assistant is ready to help!\n\n"
            "• Click a quick action button above\n"
            "• Or type your question below\n\n"
            "Examples:\n"
            "• 'Explain this XML structure'\n"
            "• 'Add a new child element called <item>'\n"
            "• 'Convert to a different namespace'"
        )
        layout.addWidget(self.chat_display, 1)
        
        # User input area
        input_layout = QHBoxLayout()
        
        self.user_input = QTextEdit()
        self.user_input.setPlaceholderText("Ask AI about your XML...")
        self.user_input.setMaximumHeight(60)
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
            self.add_ai_message("✅ Settings saved! AI assistant is now configured.")
    
    def call_ai_api(self, user_message, context_info=""):
        """Make an API call to the AI service."""
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
        
        # Add XML context if available
        if self.xml_content.strip():
            # Truncate very long XML to avoid token limits
            max_len = self.MAX_XML_CONTEXT_LENGTH
            xml_preview = self.xml_content[:max_len] if len(self.xml_content) > max_len else self.xml_content
            context_msg = f"Current XML document:\n```xml\n{xml_preview}\n```"
            if len(self.xml_content) > max_len:
                context_msg += f"\n(Truncated, full document is {len(self.xml_content)} characters)"
            messages.append({"role": "system", "content": context_msg})
        
        # Add context info if provided
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
        
        # Start the worker thread
        self.worker_thread = AIWorkerThread(
            self.settings_manager.get_api_url(),
            self.settings_manager.get_api_key(),
            self.settings_manager.get_model(),
            messages
        )
        self.worker_thread.response_ready.connect(self.on_ai_response)
        self.worker_thread.error_occurred.connect(self.on_ai_error)
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
            elif action_type == "generate":
                self.add_user_message("Help me generate XML content")
                self.add_ai_message(
                    "📝 I can help you generate XML content. Please describe what you need:\n\n"
                    "Examples:\n"
                    "• 'Create a person element with name and age'\n"
                    "• 'Add a list of products with id, name, and price'\n"
                    "• 'Generate an RSS feed structure'"
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
            elif action_type == "generate":
                self.add_user_message("Help me generate XML content")
                self.add_ai_message(
                    "📝 I can help you generate XML content. Please describe what you need:\n\n"
                    "Examples:\n"
                    "• 'Create a person element with name and age'\n"
                    "• 'Add a list of products with id, name, and price'\n"
                    "• 'Generate an RSS feed structure'\n\n"
                    "💡 Configure API settings (⚙️) for AI-powered generation!"
                )
    
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
        current_text = self.chat_display.toHtml()
        # HTML-escape user message to prevent XSS
        escaped_message = html.escape(message)
        user_html = f'<p style="color: #0066cc; margin: 5px 0;"><b>You:</b> {escaped_message}</p>'
        self.chat_display.setHtml(current_text + user_html)
        self.scroll_to_bottom()
    
    def add_ai_message(self, message):
        """Add an AI message to the chat display."""
        current_text = self.chat_display.toHtml()
        # HTML-escape message to prevent XSS, then convert newlines to breaks
        escaped_message = html.escape(message)
        formatted = escaped_message.replace('\n', '<br>')
        ai_html = f'<p style="color: #333333; margin: 5px 0; background-color: #f5f5f5; padding: 8px; border-radius: 5px;"><b>🤖 AI:</b><br>{formatted}</p>'
        self.chat_display.setHtml(current_text + ai_html)
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll chat display to bottom."""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_chat(self):
        """Clear the chat history."""
        self.chat_display.clear()
        self.add_ai_message(
            "👋 Chat cleared! I'm ready to help with your XML editing tasks."
        )
