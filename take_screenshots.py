#!/usr/bin/env python3
"""
Script to take screenshots of the XML Editor with XQuery panel.
This script should be run with QT_QPA_PLATFORM=offscreen for headless screenshot capture.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from xmleditor.main_window import MainWindow

def take_screenshots():
    """Take screenshots of the XML Editor with XQuery panel."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    window.resize(1400, 900)
    window.show()
    
    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    screenshots_taken = []
    
    def step1_load_xml():
        """Step 1: Load sample XML file"""
        print("Step 1: Loading sample XML...")
        try:
            window.load_file("/tmp/xquery_test/sample.xml")
        except Exception as e:
            print(f"  Warning: {e}")
        QTimer.singleShot(800, step2_open_xquery_panel)
    
    def step2_open_xquery_panel():
        """Step 2: Open XQuery panel"""
        print("Step 2: Opening XQuery panel...")
        try:
            window.toggle_xquery_panel()
            # Resize the dock to be more visible
            window.xquery_dock.resize(600, 900)
        except Exception as e:
            print(f"  Warning: {e}")
        QTimer.singleShot(800, step3_load_query)
    
    def step3_load_query():
        """Step 3: Load sample query"""
        print("Step 3: Loading sample query...")
        try:
            window.xquery_panel.load_file("/tmp/xquery_test/sample.xq")
        except Exception as e:
            print(f"  Warning: {e}")
        QTimer.singleShot(800, step4_take_screenshot_before)
    
    def step4_take_screenshot_before():
        """Step 4: Take screenshot before execution"""
        print("Step 4: Taking screenshot - XQuery panel with query...")
        try:
            pixmap = window.grab()
            path = os.path.join(screenshot_dir, "xquery_panel_with_query.png")
            pixmap.save(path)
            screenshots_taken.append(path)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  Error: {e}")
        QTimer.singleShot(800, step5_execute_query)
    
    def step5_execute_query():
        """Step 5: Execute the query"""
        print("Step 5: Executing query...")
        try:
            window.xquery_panel.execute_query()
        except Exception as e:
            print(f"  Warning: {e}")
        QTimer.singleShot(800, step6_take_screenshot_after)
    
    def step6_take_screenshot_after():
        """Step 6: Take screenshot after execution"""
        print("Step 6: Taking screenshot - XQuery results...")
        try:
            pixmap = window.grab()
            path = os.path.join(screenshot_dir, "xquery_panel_with_results.png")
            pixmap.save(path)
            screenshots_taken.append(path)
            print(f"  Saved: {path}")
        except Exception as e:
            print(f"  Error: {e}")
        QTimer.singleShot(500, finish)
    
    def finish():
        """Finish and exit"""
        print("\nScreenshots completed!")
        print("Screenshots saved:")
        for path in screenshots_taken:
            print(f"  - {path}")
        app.quit()
    
    # Start the sequence
    QTimer.singleShot(500, step1_load_xml)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    take_screenshots()
