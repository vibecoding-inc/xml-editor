"""
XPath query dialog for searching XML documents.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt
from xmleditor.xml_utils import XMLUtilities


class XPathDialog(QDialog):
    """Dialog for executing XPath queries."""
    
    def __init__(self, xml_content: str, parent=None):
        super().__init__(parent)
        self.xml_content = xml_content
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("XPath Query")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
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
        self.xpath_input.setToolTip(examples)
        
    def execute_query(self):
        """Execute the XPath query."""
        xpath_expr = self.xpath_input.text().strip()
        
        if not xpath_expr:
            QMessageBox.warning(self, "Warning", "Please enter an XPath expression")
            return
        
        try:
            results = XMLUtilities.xpath_query(self.xml_content, xpath_expr)
            
            if results:
                self.results_display.setPlainText("\n".join(results))
            else:
                self.results_display.setPlainText("No results found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"XPath query failed:\n{str(e)}")
            self.results_display.setPlainText(f"Error: {str(e)}")
