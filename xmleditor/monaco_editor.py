"""
Monaco Editor widget using QWebEngineView for collaborative editing.
"""

import os
from PyQt6.QtCore import QObject, QUrl, pyqtSlot, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from xmleditor.theme_manager import ThemeType


class MonacoCallHandler(QObject):
    """Handler for callbacks from Monaco editor JavaScript."""
    
    # Signals
    contentChanged = pyqtSignal(str)
    editorReady = pyqtSignal()
    collaborationStatus = pyqtSignal(str)
    collaborationError = pyqtSignal(str)
    
    @pyqtSlot()
    def onEditorReady(self):
        """Called when Monaco editor is ready."""
        print("[VERBOSE] Python: onEditorReady called")
        self.editorReady.emit()
    
    @pyqtSlot(str)
    def onContentChanged(self, content):
        """Called when editor content changes."""
        print(f"[VERBOSE] Python: onContentChanged called, content length: {len(content)}")
        self.contentChanged.emit(content)
    
    @pyqtSlot(str)
    def onCollaborationStatus(self, status):
        """Called when collaboration status changes."""
        print(f"[VERBOSE] Python: onCollaborationStatus called: {status}")
        self.collaborationStatus.emit(status)
    
    @pyqtSlot(str)
    def onCollaborationError(self, error):
        """Called when collaboration error occurs."""
        print(f"[VERBOSE] Python: onCollaborationError called: {error}")
        self.collaborationError.emit(error)


class MonacoEditor(QWidget):
    """Monaco editor widget with collaborative editing support."""
    
    # Signals
    textChanged = pyqtSignal()
    editorReady = pyqtSignal()
    collaborationStatus = pyqtSignal(str)
    collaborationError = pyqtSignal(str)
    
    def __init__(self, parent=None, theme_type=ThemeType.SYSTEM):
        super().__init__(parent)
        
        self.theme_type = theme_type
        self._is_ready = False
        self._pending_content = None
        self._pending_theme = None
        self._suppress_change_signal = False
        self._current_content = ""  # Cache of current content
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web view
        self.web_view = QWebEngineView()
        
        # Enable remote content loading
        print("[VERBOSE] Python: Configuring web view settings...")
        from PyQt6.QtWebEngineCore import QWebEngineSettings
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        print("[VERBOSE] Python: LocalContentCanAccessRemoteUrls enabled")
        print("[VERBOSE] Python: LocalContentCanAccessFileUrls enabled")
        
        layout.addWidget(self.web_view)
        
        # Set up web channel for Python-JS communication
        self.channel = QWebChannel()
        self.handler = MonacoCallHandler()
        self.channel.registerObject('backend', self.handler)
        self.web_view.page().setWebChannel(self.channel)
        
        # Connect signals
        self.handler.editorReady.connect(self._on_editor_ready)
        self.handler.contentChanged.connect(self._on_content_changed)
        self.handler.collaborationStatus.connect(self.collaborationStatus.emit)
        self.handler.collaborationError.connect(self.collaborationError.emit)
        
        # Load the HTML file
        self._load_monaco_editor()
    
    def _load_monaco_editor(self):
        """Load the Monaco editor HTML."""
        print("[VERBOSE] Python: Loading Monaco editor HTML...")
        # Get the path to the HTML file
        resources_dir = os.path.join(os.path.dirname(__file__), 'resources')
        html_path = os.path.join(resources_dir, 'monaco_editor.html')
        
        print(f"[VERBOSE] Python: Resources dir: {resources_dir}")
        print(f"[VERBOSE] Python: HTML path: {html_path}")
        print(f"[VERBOSE] Python: HTML file exists: {os.path.exists(html_path)}")
        
        if os.path.exists(html_path):
            url = QUrl.fromLocalFile(html_path)
            print(f"[VERBOSE] Python: Loading URL: {url.toString()}")
            self.web_view.setUrl(url)
        else:
            print("[VERBOSE] Python: ERROR - HTML file not found!")
            # Fallback: load inline HTML
            self.web_view.setHtml('<html><body><h1>Monaco Editor not found</h1></body></html>')
    
    def _on_editor_ready(self):
        """Handle editor ready event."""
        print("[VERBOSE] Python: _on_editor_ready called")
        self._is_ready = True
        print(f"[VERBOSE] Python: Editor is now ready, pending content: {self._pending_content is not None}")
        
        # Apply pending operations
        if self._pending_content is not None:
            print("[VERBOSE] Python: Applying pending content...")
            self._set_content_internal(self._pending_content)
            self._pending_content = None
        
        if self._pending_theme is not None:
            print("[VERBOSE] Python: Applying pending theme...")
            self._set_theme_internal(self._pending_theme)
            self._pending_theme = None
        
        print("[VERBOSE] Python: Emitting editorReady signal")
        self.editorReady.emit()
    
    def _on_content_changed(self, content):
        """Handle content changed event from editor."""
        self._current_content = content  # Update cached content
        print(f"[VERBOSE] Python: Content changed, length: {len(content)}, suppress signal: {self._suppress_change_signal}")
        if not self._suppress_change_signal:
            self.textChanged.emit()
    
    def get_text(self):
        """Get the text content of the editor (returns cached content)."""
        return self._current_content
    
    def set_text(self, text):
        """Set the text content of the editor."""
        self._current_content = text  # Update cache immediately
        if self._is_ready:
            self._set_content_internal(text)
        else:
            self._pending_content = text
    
    def _set_content_internal(self, text):
        """Internal method to set content via JavaScript."""
        self._suppress_change_signal = True
        # Properly escape content using JSON encoding
        import json
        escaped_text = json.dumps(text)
        js_code = f'window.monacoEditor.setContent({escaped_text});'
        self.web_view.page().runJavaScript(js_code)
        self._suppress_change_signal = False
    
    def apply_theme(self, theme_type):
        """Apply a theme to the editor."""
        self.theme_type = theme_type
        
        # Map theme types to Monaco themes
        theme_map = {
            ThemeType.LIGHT: 'vs',
            ThemeType.DARK: 'vs-dark',
            ThemeType.SYSTEM: 'vs-dark',  # Default to dark
            ThemeType.CATPPUCCIN_MOCHA: 'vs-dark',
            ThemeType.CATPPUCCIN_LATTE: 'vs',
            ThemeType.DRACULA: 'vs-dark',
            ThemeType.SOLARIZED_LIGHT: 'vs',
            ThemeType.SOLARIZED_DARK: 'vs-dark',
            ThemeType.NORD: 'vs-dark',
            ThemeType.GRUVBOX_LIGHT: 'vs',
            ThemeType.GRUVBOX_DARK: 'vs-dark',
        }
        
        monaco_theme = theme_map.get(theme_type, 'vs-dark')
        
        if self._is_ready:
            self._set_theme_internal(monaco_theme)
        else:
            self._pending_theme = monaco_theme
    
    def _set_theme_internal(self, monaco_theme):
        """Internal method to set theme via JavaScript."""
        js_code = f'window.monacoEditor.setTheme("{monaco_theme}");'
        self.web_view.page().runJavaScript(js_code)
    
    def setWrapMode(self, wrap_mode):
        """Set word wrap mode."""
        # For compatibility with QScintilla interface
        from PyQt6.Qsci import QsciScintilla
        enabled = wrap_mode != QsciScintilla.WrapMode.WrapNone
        self.set_word_wrap(enabled)
    
    def set_word_wrap(self, enabled):
        """Set word wrap enabled/disabled."""
        if self._is_ready:
            js_code = f'window.monacoEditor.setWordWrap({str(enabled).lower()});'
            self.web_view.page().runJavaScript(js_code)
    
    def connect_collaboration(self, server_url, room_name):
        """Connect to collaboration server."""
        if self._is_ready:
            js_code = f'window.monacoEditor.connectCollaboration("{server_url}", "{room_name}");'
            self.web_view.page().runJavaScript(js_code)
    
    def disconnect_collaboration(self):
        """Disconnect from collaboration server."""
        if self._is_ready:
            js_code = 'window.monacoEditor.disconnectCollaboration();'
            self.web_view.page().runJavaScript(js_code)
    
    def is_collaboration_active(self, callback):
        """Check if collaboration is active (async with callback)."""
        if self._is_ready:
            js_code = 'window.monacoEditor.isCollaborationActive();'
            self.web_view.page().runJavaScript(js_code, callback)
    
    # Compatibility methods for QScintilla interface
    def text(self):
        """Get text (compatibility method)."""
        return self.get_text()
    
    def setText(self, text):
        """Set text (compatibility method)."""
        self.set_text(text)
    
    def clear(self):
        """Clear editor content."""
        self.set_text('')
    
    def undo(self):
        """Undo (not implemented for Monaco)."""
        pass
    
    def redo(self):
        """Redo (not implemented for Monaco)."""
        pass
    
    def cut(self):
        """Cut (not implemented for Monaco)."""
        pass
    
    def copy(self):
        """Copy (not implemented for Monaco)."""
        pass
    
    def paste(self):
        """Paste (not implemented for Monaco)."""
        pass
    
    def hasSelectedText(self):
        """Check if text is selected."""
        return False
    
    def selectedText(self):
        """Get selected text."""
        return ""
    
    def getSelection(self):
        """Get selection range."""
        return (0, 0, 0, 0)
    
    def getCursorPosition(self):
        """Get cursor position."""
        return (0, 0)
    
    def setSelection(self, line_from, index_from, line_to, index_to):
        """Set selection."""
        pass
    
    def replaceSelectedText(self, text):
        """Replace selected text."""
        pass
    
    def findFirst(self, expr, re, cs, wo, wrap, forward=True):
        """Find text (not implemented)."""
        return False
