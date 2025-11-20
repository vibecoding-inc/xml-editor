"""
Schema generation dialog for generating XSD and DTD from XML.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QTextEdit, QPushButton, QTabWidget, QFileDialog,
                              QMessageBox, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from xmleditor.xml_utils import XMLUtilities


class SchemaGenerationDialog(QDialog):
    """Dialog for generating schemas from XML."""
    
    def __init__(self, xml_content: str, parent=None):
        super().__init__(parent)
        self.xml_content = xml_content
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Generate Schema")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("Generate XSD or DTD schema from the current XML document:")
        layout.addWidget(info_label)
        
        # Tab widget for different schema types
        self.tab_widget = QTabWidget()
        
        # XSD generation tab
        self.xsd_tab = self.create_xsd_tab()
        self.tab_widget.addTab(self.xsd_tab, "XSD Schema")
        
        # DTD generation tab
        self.dtd_tab = self.create_dtd_tab()
        self.tab_widget.addTab(self.dtd_tab, "DTD")
        
        layout.addWidget(self.tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def create_xsd_tab(self):
        """Create XSD generation tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Info
        layout.addWidget(QLabel("Generated XSD Schema:"))
        
        # Schema output
        self.xsd_output = QTextEdit()
        self.xsd_output.setReadOnly(True)
        font = QFont("Courier New", 9)
        self.xsd_output.setFont(font)
        layout.addWidget(self.xsd_output)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Schema")
        generate_btn.clicked.connect(self.generate_xsd)
        button_layout.addWidget(generate_btn)
        
        save_btn = QPushButton("Save to File")
        save_btn.clicked.connect(self.save_xsd)
        button_layout.addWidget(save_btn)
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_xsd)
        button_layout.addWidget(copy_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_dtd_tab(self):
        """Create DTD generation tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Info
        layout.addWidget(QLabel("Generated DTD:"))
        
        # Schema output
        self.dtd_output = QTextEdit()
        self.dtd_output.setReadOnly(True)
        font = QFont("Courier New", 9)
        self.dtd_output.setFont(font)
        layout.addWidget(self.dtd_output)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Schema")
        generate_btn.clicked.connect(self.generate_dtd)
        button_layout.addWidget(generate_btn)
        
        save_btn = QPushButton("Save to File")
        save_btn.clicked.connect(self.save_dtd)
        button_layout.addWidget(save_btn)
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_dtd)
        button_layout.addWidget(copy_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def generate_xsd(self):
        """Generate XSD schema from XML."""
        try:
            schema = XMLUtilities.generate_xsd_schema(self.xml_content)
            self.xsd_output.setPlainText(schema)
            self.xsd_output.setStyleSheet("")
        except Exception as e:
            self.xsd_output.setStyleSheet("color: red;")
            self.xsd_output.setPlainText(f"Error generating XSD schema:\n{str(e)}")
    
    def generate_dtd(self):
        """Generate DTD from XML."""
        try:
            schema = XMLUtilities.generate_dtd_schema(self.xml_content)
            self.dtd_output.setPlainText(schema)
            self.dtd_output.setStyleSheet("")
        except Exception as e:
            self.dtd_output.setStyleSheet("color: red;")
            self.dtd_output.setPlainText(f"Error generating DTD:\n{str(e)}")
    
    def save_xsd(self):
        """Save XSD schema to file."""
        content = self.xsd_output.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "Please generate a schema first")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save XSD Schema", "", "XSD Files (*.xsd);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", f"Schema saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def save_dtd(self):
        """Save DTD to file."""
        content = self.dtd_output.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "Please generate a schema first")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save DTD", "", "DTD Files (*.dtd);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", f"DTD saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def copy_xsd(self):
        """Copy XSD schema to clipboard."""
        content = self.xsd_output.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "Please generate a schema first")
            return
        
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        QMessageBox.information(self, "Success", "Schema copied to clipboard")
    
    def copy_dtd(self):
        """Copy DTD to clipboard."""
        content = self.dtd_output.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "Please generate a schema first")
            return
        
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        QMessageBox.information(self, "Success", "DTD copied to clipboard")
