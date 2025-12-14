"""
XQuery panel for executing XQuery expressions with file-based editor.
"""

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTextEdit, QFileDialog, QMessageBox,
                              QSplitter, QFrame, QLineEdit, QTextEdit, QTextBrowser, QTabWidget)
from PyQt6.QtCore import Qt, QTimer, QFileSystemWatcher
from PyQt6.QtGui import QFont, QColor, QTextCursor
from PyQt6.Qsci import QsciScintilla
from lxml import etree
from xmleditor.xml_utils import XMLUtilities
from xmleditor.theme_manager import ThemeManager, ThemeType


class XQueryEditor(QsciScintilla):
    """Simple code editor for XQuery files with basic syntax highlighting."""
    
    def __init__(self, parent=None, theme_type=ThemeType.SYSTEM):
        super().__init__(parent)
        
        # Set up the font
        self.font = QFont("Courier New", 10)
        self.font.setFixedPitch(True)
        self.setFont(self.font)
        self.setMarginsFont(self.font)
        
        # Store theme type
        self.theme_type = theme_type
        
        # Set up line numbers
        fontmetrics = self.fontMetrics()
        self.setMarginsFont(self.font)
        self.setMarginWidth(0, fontmetrics.horizontalAdvance("00000") + 6)
        self.setMarginLineNumbers(0, True)
        
        # Set indentation
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setAutoIndent(True)
        
        # Set folding
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        
        # Set caret
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        
        # Set edge mode
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(80)
        
        # Enable brace matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        
        # Enable UTF-8
        self.setUtf8(True)
        
        # Set EOL mode to Unix
        self.setEolMode(QsciScintilla.EolMode.EolUnix)
        self.setEolVisibility(False)
        
        # Enable word wrap
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)
        
        # Apply theme
        self.apply_theme(theme_type)
    
    def apply_theme(self, theme_type):
        """Apply a theme to the editor."""
        self.theme_type = theme_type
        theme = ThemeManager.get_theme(theme_type)
        
        # Set colors
        self.setCaretForegroundColor(QColor(theme.get_color("text")))
        self.setCaretLineBackgroundColor(QColor(theme.get_color("caret_line")))
        
        # Set margin colors
        self.setMarginsBackgroundColor(QColor(theme.get_color("surface0")))
        self.setMarginsForegroundColor(QColor(theme.get_color("subtext1")))
        
        # Set selection colors
        self.setSelectionBackgroundColor(QColor(theme.get_color("selection")))
        self.setSelectionForegroundColor(QColor(theme.get_color("text")))
        
        # Set matched brace colors
        self.setMatchedBraceBackgroundColor(QColor(theme.get_color("matched_brace")))
        self.setMatchedBraceForegroundColor(QColor(theme.get_color("text")))
        
        # Set unmatched brace colors  
        self.setUnmatchedBraceForegroundColor(QColor(theme.get_color("red")))
        
        # Set general editor colors
        self.setPaper(QColor(theme.get_color("base")))
        self.setColor(QColor(theme.get_color("text")))
        
        # Set edge color
        self.setEdgeColor(QColor(theme.get_color("edge_color")))
    
    def get_text(self):
        """Get editor text."""
        return self.text()
    
    def set_text(self, text):
        """Set editor text."""
        self.setText(text)


class XQueryPanel(QWidget):
    """Panel for XQuery execution with file-based editor."""
    
    def __init__(self, parent=None, theme_type=ThemeType.SYSTEM, get_xml_callback=None):
        super().__init__(parent)
        self.theme_type = theme_type
        self.get_xml_callback = get_xml_callback  # Callback to get current XML
        self.xquery_file_path = None
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.on_file_changed)
        
        # Configuration constants
        self.MAX_RESULT_DISPLAY_LENGTH = 500  # Maximum characters to display per result
        
        # Timer for auto-save
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_file)
        self.save_delay = 1000  # 1 second delay after typing stops
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create splitter for top/bottom layout
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section - XQuery editor
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # File picker section
        file_section = QFrame()
        file_section.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        file_layout = QHBoxLayout(file_section)
        file_layout.setContentsMargins(5, 5, 5, 5)
        
        file_layout.addWidget(QLabel("XQuery File:"))
        
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        self.file_path_display.setPlaceholderText("No file selected - choose a .xq or .xquery file")
        file_layout.addWidget(self.file_path_display)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        new_file_btn = QPushButton("New File...")
        new_file_btn.clicked.connect(self.create_new_file)
        file_layout.addWidget(new_file_btn)
        
        top_layout.addWidget(file_section)
        
        # XQuery editor
        top_layout.addWidget(QLabel("XQuery Expression (XPath 3.0):"))
        self.xquery_editor = XQueryEditor(theme_type=self.theme_type)
        # Note: QScintilla doesn't support setPlaceholderText
        # Users can start typing or load a file to populate the editor
        self.xquery_editor.textChanged.connect(self.on_text_changed)
        top_layout.addWidget(self.xquery_editor)
        
        # Execute button
        execute_btn = QPushButton("Execute Query")
        execute_btn.clicked.connect(self.execute_query)
        top_layout.addWidget(execute_btn)
        
        splitter.addWidget(top_widget)
        
        # Bottom section - Results display
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # Status bar at the top
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 4, 8, 4)
        
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.result_count_label = QLabel("")
        status_layout.addWidget(self.result_count_label)
        
        bottom_layout.addWidget(status_frame)
        
        # Results list widget
        results_label = QLabel("Result:")
        bottom_layout.addWidget(results_label)
        
        self.result_tabs = QTabWidget()
        
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        font = QFont("Courier New", 10)
        self.result_view.setFont(font)
        self.result_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.result_tabs.addTab(self.result_view, "Source")
        
        self.html_view = QTextBrowser()
        self.html_view.setOpenExternalLinks(False)
        self.html_view.setOpenLinks(False)
        self.result_tabs.addTab(self.html_view, "HTML")
        
        bottom_layout.addWidget(self.result_tabs)
        
        splitter.addWidget(bottom_widget)
        
        # Set initial splitter sizes (60% editor, 40% results)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
    
    def browse_file(self):
        """Browse for an XQuery file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select XQuery File",
            "",
            "XQuery Files (*.xq *.xquery);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def create_new_file(self):
        """Create a new XQuery file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Create New XQuery File",
            "",
            "XQuery Files (*.xq *.xquery);;All Files (*)"
        )
        
        if file_path:
            # Add extension if not present
            if not file_path.endswith(('.xq', '.xquery')):
                file_path += '.xq'
            
            # Create the file
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("(: XQuery expression :)\n")
                self.load_file(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create file:\n{str(e)}")
    
    def load_file(self, file_path):
        """Load an XQuery file into the editor."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Stop watching old file
            if self.xquery_file_path:
                try:
                    self.file_watcher.removePath(self.xquery_file_path)
                except:
                    pass  # Path may not be watched, ignore
            
            # Set new file
            self.xquery_file_path = file_path
            self.file_path_display.setText(file_path)
            self.xquery_editor.set_text(content)
            
            # Watch new file for external changes
            self.file_watcher.addPath(file_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def on_file_changed(self, path):
        """Handle external file changes."""
        if path == self.xquery_file_path and os.path.exists(path):
            # File was modified externally, reload it
            reply = QMessageBox.question(
                self,
                "File Changed",
                f"The file {os.path.basename(path)} has been modified externally.\nReload it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.xquery_editor.set_text(content)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to reload file:\n{str(e)}")
    
    def on_text_changed(self):
        """Handle text changes in the editor."""
        if self.xquery_file_path:
            # Start/restart auto-save timer
            self.save_timer.start(self.save_delay)
    
    def save_file(self):
        """Save the current content to file."""
        if not self.xquery_file_path:
            return
        
        try:
            # Temporarily stop watching to avoid triggering our own change
            try:
                self.file_watcher.removePath(self.xquery_file_path)
            except:
                pass  # Path may not be watched, ignore
            
            with open(self.xquery_file_path, 'w', encoding='utf-8') as f:
                f.write(self.xquery_editor.get_text())
            
            # Resume watching
            self.file_watcher.addPath(self.xquery_file_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def execute_query(self):
        """Execute the XQuery expression."""
        xquery = self.xquery_editor.get_text().strip()
        
        if not xquery:
            self.show_error("No XQuery expression provided")
            return
        
        # Get the current XML content
        xml_content = None
        if self.get_xml_callback:
            xml_content = self.get_xml_callback()
        
        if not xml_content or not xml_content.strip():
            self.show_error("No XML document is currently open")
            return
        
        # Execute the query
        success, message, result_xml = XMLUtilities.execute_xquery(xml_content, xquery)
        
        if success:
            self.show_results(message, result_xml)
        else:
            self.show_error(message)
    
    def show_error(self, message):
        """Display an error message."""
        theme = ThemeManager.get_theme(self.theme_type)
        self.status_label.setText("Error")
        self.status_label.setStyleSheet(f"font-weight: bold; color: {theme.get_color('red')};")
        self.result_count_label.setText("")
        
        self.result_view.setPlainText(f"❌ {message}")
        self.html_view.setHtml(f"<p style='color:red;'>❌ {message}</p>")
    
    def show_results(self, message, result_xml: str):
        """Display query results."""
        theme = ThemeManager.get_theme(self.theme_type)
        
        pretty_result = result_xml.strip()
        
        self.status_label.setText("Success")
        self.status_label.setStyleSheet(f"font-weight: bold; color: {theme.get_color('green')};")
        self.result_count_label.setText("")
        
        display_text = pretty_result
        self.result_view.setPlainText(display_text)
        self.result_view.moveCursor(QTextCursor.MoveOperation.Start)
        
        # Render HTML view
        self.html_view.setHtml(result_xml)
    
    def apply_theme(self, theme_type):
        """Apply theme to the panel."""
        self.theme_type = theme_type
        if hasattr(self, 'xquery_editor'):
            self.xquery_editor.apply_theme(theme_type)
