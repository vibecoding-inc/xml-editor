"""
XPath query dialog for searching XML documents.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QTextEdit, QMessageBox,
                              QFrame)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont
from xmleditor.xml_utils import XMLUtilities


class XPathDialog(QDialog):
    """Dialog for executing XPath queries."""
    
    SETTINGS_KEY_XPATH_EXPRESSION = "xpath_expression"
    
    def __init__(self, xml_content: str, context_xpath: str = "", parent=None, settings: QSettings = None):
        super().__init__(parent)
        self.xml_content = xml_content
        self.context_xpath = context_xpath
        self.settings = settings
        self.init_ui()
        self._load_xpath_expression()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("XPath Query")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Context node indicator (shown when a node is selected in tree view)
        if self.context_xpath:
            self.context_frame = QFrame()
            self.context_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
            self.context_frame.setStyleSheet(
                "QFrame { background-color: #e3f2fd; border: 1px solid #2196f3; "
                "border-radius: 4px; padding: 4px; }"
            )
            
            context_layout = QHBoxLayout(self.context_frame)
            context_layout.setContentsMargins(8, 4, 8, 4)
            
            # Icon/indicator - using text for better accessibility
            context_icon = QLabel("●")
            context_icon.setStyleSheet("color: #1565c0; font-size: 14px;")
            context_icon.setFixedWidth(20)
            context_layout.addWidget(context_icon)
            
            # Context info
            context_info_layout = QVBoxLayout()
            context_info_layout.setSpacing(0)
            
            context_label = QLabel("Context Node Selected")
            context_label.setStyleSheet("font-weight: bold; color: #1565c0;")
            context_info_layout.addWidget(context_label)
            
            self.context_path_label = QLabel(self.context_xpath)
            self.context_path_label.setStyleSheet("color: #424242; font-family: monospace;")
            self.context_path_label.setWordWrap(True)
            context_info_layout.addWidget(self.context_path_label)
            
            context_layout.addLayout(context_info_layout, 1)
            
            # Clear context button
            clear_btn = QPushButton("Use Document Root")
            clear_btn.setToolTip("Execute query from document root instead")
            clear_btn.clicked.connect(self._clear_context)
            context_layout.addWidget(clear_btn)
            
            layout.addWidget(self.context_frame)
        
        # XPath input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("XPath Expression:"))
        self.xpath_input = QLineEdit()
        self.xpath_input.setPlaceholderText("e.g., //book[@category='web']")
        self.xpath_input.returnPressed.connect(self.execute_query)
        input_layout.addWidget(self.xpath_input)
        
        # Execute button
        self.execute_btn = QPushButton("Execute")
        self.execute_btn.clicked.connect(self.execute_query)
        input_layout.addWidget(self.execute_btn)
        
        layout.addLayout(input_layout)
        
        # Results display
        layout.addWidget(QLabel("Results:"))
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Add some example queries in tooltip
        examples = (
            "Examples:\n"
            "//element - All elements with name 'element'\n"
            "/root/child - Direct children\n"
            "//element[@attribute='value'] - Filter by attribute\n"
            "//element[text()='value'] - Filter by text content\n"
            "//element[position()=1] - First element\n"
            "count(//element) - Count elements"
        )
        if self.context_xpath:
            examples += "\n\nNote: Queries run relative to selected context node.\n"
            examples += "Use './/element' for descendants of context node."
        self.xpath_input.setToolTip(examples)
    
    def _clear_context(self):
        """Clear the context node and hide the indicator."""
        self.context_xpath = ""
        if hasattr(self, 'context_frame'):
            self.context_frame.hide()
        
    def execute_query(self):
        """Execute the XPath query."""
        xpath_expr = self.xpath_input.text().strip()
        
        if not xpath_expr:
            QMessageBox.warning(self, "Warning", "Please enter an XPath expression")
            return
        
        try:
            results = XMLUtilities.xpath_query(
                self.xml_content, 
                xpath_expr, 
                self.context_xpath
            )
            
            if results:
                self.results_display.setPlainText("\n".join(results))
            else:
                self.results_display.setPlainText("No results found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"XPath query failed:\n{str(e)}")
            self.results_display.setPlainText(f"Error: {str(e)}")
    
    def _load_xpath_expression(self):
        """Load the saved XPath expression from settings."""
        if self.settings:
            saved_xpath = self.settings.value(self.SETTINGS_KEY_XPATH_EXPRESSION, "")
            if isinstance(saved_xpath, str) and saved_xpath.strip():
                self.xpath_input.setText(saved_xpath)
    
    def _save_xpath_expression(self):
        """Save the current XPath expression to settings."""
        if self.settings:
            self.settings.setValue(self.SETTINGS_KEY_XPATH_EXPRESSION, self.xpath_input.text())
    
    def accept(self):
        """Override accept to save XPath expression before closing."""
        self._save_xpath_expression()
        super().accept()
    
    def reject(self):
        """Override reject to save XPath expression before closing."""
        self._save_xpath_expression()
        super().reject()
