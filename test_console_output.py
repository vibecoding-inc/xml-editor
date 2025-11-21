#!/usr/bin/env python3
"""
Test to capture console output from Monaco editor.
"""

import sys
import os
sys.path.insert(0, '/home/runner/work/xml-editor/xml-editor')

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtWebEngineCore import QWebEnginePage
from xmleditor.main_window import MainWindow

class ConsoleCapturePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"JS [{level}] Line {lineNumber}: {message}")

def test_console():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Replace the page with one that captures console
    editor = window.get_current_editor()
    if hasattr(editor, 'web_view'):
        page = ConsoleCapturePage(editor.web_view)
        editor.web_view.setPage(page)
    
    # Load sample content
    xsd_path = "/home/runner/work/xml-editor/xml-editor/samples/books.xsd"
    with open(xsd_path, 'r') as f:
        content = f.read()
    
    if editor:
        editor.set_text(content)
    
    window.show()
    window.resize(1200, 800)
    
    def quit_app():
        print("Quitting...")
        app.quit()
    
    # Wait a bit for messages, then quit
    QTimer.singleShot(3000, quit_app)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_console())
