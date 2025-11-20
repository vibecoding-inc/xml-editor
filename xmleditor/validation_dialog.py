"""
Validation dialog for XML schema validation.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QTextEdit, QPushButton, QTabWidget, QFileDialog,
                              QMessageBox, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from xmleditor.xml_utils import XMLUtilities


class ValidationDialog(QDialog):
    """Dialog for validating XML against schemas."""
    
    def __init__(self, xml_content: str, parent=None):
        super().__init__(parent)
        self.xml_content = xml_content
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("XML Validation")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout()
        
        # Tab widget for different validation types
        self.tab_widget = QTabWidget()
        
        # Well-formedness check tab
        self.well_formed_tab = self.create_well_formed_tab()
        self.tab_widget.addTab(self.well_formed_tab, "Well-Formedness")
        
        # XSD validation tab
        self.xsd_tab = self.create_xsd_tab()
        self.tab_widget.addTab(self.xsd_tab, "XSD Schema")
        
        # DTD validation tab
        self.dtd_tab = self.create_dtd_tab()
        self.tab_widget.addTab(self.dtd_tab, "DTD")
        
        layout.addWidget(self.tab_widget)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Auto-validate well-formedness
        self.validate_well_formed()
        
    def create_well_formed_tab(self):
        """Create well-formedness check tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Well-Formedness Check:"))
        
        self.well_formed_result = QTextEdit()
        self.well_formed_result.setReadOnly(True)
        layout.addWidget(self.well_formed_result)
        
        validate_btn = QPushButton("Validate")
        validate_btn.clicked.connect(self.validate_well_formed)
        layout.addWidget(validate_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_xsd_tab(self):
        """Create XSD validation tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Schema input
        layout.addWidget(QLabel("XSD Schema:"))
        
        schema_buttons = QHBoxLayout()
        load_schema_btn = QPushButton("Load Schema File")
        load_schema_btn.clicked.connect(self.load_xsd_file)
        schema_buttons.addWidget(load_schema_btn)
        schema_buttons.addStretch()
        layout.addLayout(schema_buttons)
        
        self.xsd_input = QTextEdit()
        self.xsd_input.setPlaceholderText("Paste XSD schema here or load from file...")
        font = QFont("Courier New", 9)
        self.xsd_input.setFont(font)
        layout.addWidget(self.xsd_input)
        
        # Validation result
        layout.addWidget(QLabel("Validation Result:"))
        self.xsd_result = QTextEdit()
        self.xsd_result.setReadOnly(True)
        layout.addWidget(self.xsd_result)
        
        validate_btn = QPushButton("Validate")
        validate_btn.clicked.connect(self.validate_xsd)
        layout.addWidget(validate_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_dtd_tab(self):
        """Create DTD validation tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # DTD input
        layout.addWidget(QLabel("DTD:"))
        
        dtd_buttons = QHBoxLayout()
        load_dtd_btn = QPushButton("Load DTD File")
        load_dtd_btn.clicked.connect(self.load_dtd_file)
        dtd_buttons.addWidget(load_dtd_btn)
        dtd_buttons.addStretch()
        layout.addLayout(dtd_buttons)
        
        self.dtd_input = QTextEdit()
        self.dtd_input.setPlaceholderText("Paste DTD here or load from file...")
        font = QFont("Courier New", 9)
        self.dtd_input.setFont(font)
        layout.addWidget(self.dtd_input)
        
        # Validation result
        layout.addWidget(QLabel("Validation Result:"))
        self.dtd_result = QTextEdit()
        self.dtd_result.setReadOnly(True)
        layout.addWidget(self.dtd_result)
        
        validate_btn = QPushButton("Validate")
        validate_btn.clicked.connect(self.validate_dtd)
        layout.addWidget(validate_btn)
        
        widget.setLayout(layout)
        return widget
    
    def validate_well_formed(self):
        """Validate XML well-formedness."""
        is_valid, message = XMLUtilities.validate_xml(self.xml_content)
        
        if is_valid:
            self.well_formed_result.setStyleSheet("color: green;")
            self.well_formed_result.setPlainText(f"✓ {message}")
        else:
            self.well_formed_result.setStyleSheet("color: red;")
            self.well_formed_result.setPlainText(f"✗ {message}")
    
    def validate_xsd(self):
        """Validate XML against XSD schema."""
        xsd_content = self.xsd_input.toPlainText().strip()
        
        if not xsd_content:
            QMessageBox.warning(self, "Warning", "Please provide an XSD schema")
            return
        
        try:
            is_valid, message = XMLUtilities.validate_with_xsd(self.xml_content, xsd_content)
            
            if is_valid:
                self.xsd_result.setStyleSheet("color: green;")
                self.xsd_result.setPlainText(f"✓ {message}")
            else:
                self.xsd_result.setStyleSheet("color: red;")
                self.xsd_result.setPlainText(f"✗ {message}")
        except Exception as e:
            self.xsd_result.setStyleSheet("color: red;")
            self.xsd_result.setPlainText(f"✗ Error: {str(e)}")
    
    def validate_dtd(self):
        """Validate XML against DTD."""
        dtd_content = self.dtd_input.toPlainText().strip()
        
        if not dtd_content:
            QMessageBox.warning(self, "Warning", "Please provide a DTD")
            return
        
        try:
            is_valid, message = XMLUtilities.validate_with_dtd(self.xml_content, dtd_content)
            
            if is_valid:
                self.dtd_result.setStyleSheet("color: green;")
                self.dtd_result.setPlainText(f"✓ {message}")
            else:
                self.dtd_result.setStyleSheet("color: red;")
                self.dtd_result.setPlainText(f"✗ {message}")
        except Exception as e:
            self.dtd_result.setStyleSheet("color: red;")
            self.dtd_result.setPlainText(f"✗ Error: {str(e)}")
    
    def load_xsd_file(self):
        """Load XSD schema from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open XSD Schema", "", "XSD Files (*.xsd);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.xsd_input.setPlainText(f.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def load_dtd_file(self):
        """Load DTD from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open DTD", "", "DTD Files (*.dtd);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.dtd_input.setPlainText(f.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
