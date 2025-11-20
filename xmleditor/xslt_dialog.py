"""
XSLT transformation dialog.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QTextEdit, QPushButton, QFileDialog, QMessageBox)
from PyQt6.QtGui import QFont
from xmleditor.xml_utils import XMLUtilities


class XSLTDialog(QDialog):
    """Dialog for applying XSLT transformations."""
    
    def __init__(self, xml_content: str, parent=None):
        super().__init__(parent)
        self.xml_content = xml_content
        self.transformed_xml = ""
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("XSLT Transformation")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # XSLT input
        layout.addWidget(QLabel("XSLT Stylesheet:"))
        
        xslt_buttons = QHBoxLayout()
        load_xslt_btn = QPushButton("Load XSLT File")
        load_xslt_btn.clicked.connect(self.load_xslt_file)
        xslt_buttons.addWidget(load_xslt_btn)
        xslt_buttons.addStretch()
        layout.addLayout(xslt_buttons)
        
        self.xslt_input = QTextEdit()
        self.xslt_input.setPlaceholderText("Paste XSLT stylesheet here or load from file...")
        font = QFont("Courier New", 9)
        self.xslt_input.setFont(font)
        layout.addWidget(self.xslt_input, 2)
        
        # Transform button
        transform_btn = QPushButton("Transform")
        transform_btn.clicked.connect(self.apply_transformation)
        layout.addWidget(transform_btn)
        
        # Result display
        layout.addWidget(QLabel("Transformation Result:"))
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setFont(font)
        layout.addWidget(self.result_display, 3)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.save_result_btn = QPushButton("Save Result")
        self.save_result_btn.clicked.connect(self.save_result)
        self.save_result_btn.setEnabled(False)
        button_layout.addWidget(self.save_result_btn)
        
        self.apply_btn = QPushButton("Apply to Editor")
        self.apply_btn.clicked.connect(self.accept)
        self.apply_btn.setEnabled(False)
        button_layout.addWidget(self.apply_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def apply_transformation(self):
        """Apply XSLT transformation."""
        xslt_content = self.xslt_input.toPlainText().strip()
        
        if not xslt_content:
            QMessageBox.warning(self, "Warning", "Please provide an XSLT stylesheet")
            return
        
        try:
            self.transformed_xml = XMLUtilities.apply_xslt(self.xml_content, xslt_content)
            self.result_display.setPlainText(self.transformed_xml)
            self.save_result_btn.setEnabled(True)
            self.apply_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Transformation failed:\n{str(e)}")
            self.result_display.setPlainText(f"Error: {str(e)}")
            self.save_result_btn.setEnabled(False)
            self.apply_btn.setEnabled(False)
    
    def load_xslt_file(self):
        """Load XSLT stylesheet from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open XSLT Stylesheet", "", "XSLT Files (*.xslt *.xsl);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.xslt_input.setPlainText(f.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def save_result(self):
        """Save transformation result to file."""
        if not self.transformed_xml:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Transformation Result", "", "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.transformed_xml)
                QMessageBox.information(self, "Success", "File saved successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def get_transformed_xml(self):
        """Get the transformed XML content."""
        return self.transformed_xml
