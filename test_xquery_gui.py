#!/usr/bin/env python3
"""
GUI test script to demonstrate XQuery panel functionality.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from xmleditor.main_window import MainWindow

def test_gui():
    """Test GUI with XQuery panel."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Load sample XML file after window is shown
    def load_sample():
        # Open sample XML
        window.load_file("/tmp/xquery_test/sample.xml")
        
        # Open XQuery panel after a delay
        QTimer.singleShot(500, lambda: window.toggle_xquery_panel())
        
        # Take screenshot after another delay
        QTimer.singleShot(1000, lambda: take_screenshot())
    
    def take_screenshot():
        """Take a screenshot of the window."""
        try:
            # Make XQuery panel more visible
            window.xquery_dock.resize(600, 800)
            
            # Take screenshot
            pixmap = window.grab()
            screenshot_path = "/tmp/xquery_panel_screenshot.png"
            pixmap.save(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            
            # Close after another delay
            QTimer.singleShot(500, lambda: app.quit())
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            app.quit()
    
    # Start the sequence
    QTimer.singleShot(200, load_sample)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_gui()
