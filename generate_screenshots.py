#!/usr/bin/env python3
"""
Generate screenshots for XQuery panel with improved UI.
Uses a step-by-step approach without event loop.
"""
import sys
import os

# Set offscreen platform before importing Qt
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication
from xmleditor.main_window import MainWindow

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create and setup window
    window = MainWindow()
    window.resize(1400, 900)
    window.show()
    
    print("Step 1: Loading sample XML file...")
    try:
        window.load_file("/tmp/xquery_test/sample.xml")
    except Exception as e:
        print(f"  Warning: {e}")
    
    print("Step 2: Opening XQuery panel...")
    try:
        window.toggle_xquery_panel()
    except Exception as e:
        print(f"  Warning: {e}")
    
    print("Step 3: Loading sample XQuery file...")
    try:
        window.xquery_panel.load_file("/tmp/xquery_test/sample.xq")
    except Exception as e:
        print(f"  Warning: {e}")
    
    print("Step 4: Taking screenshot - before execution...")
    os.makedirs("screenshots", exist_ok=True)
    pixmap = window.grab()
    pixmap.save("screenshots/xquery_panel_new_ui.png")
    print("  ✓ Saved: screenshots/xquery_panel_new_ui.png")
    
    print("Step 5: Executing query...")
    try:
        window.xquery_panel.execute_query()
    except Exception as e:
        print(f"  Warning: {e}")
    
    print("Step 6: Taking screenshot - after execution...")
    pixmap = window.grab()
    pixmap.save("screenshots/xquery_panel_with_results_new.png")
    print("  ✓ Saved: screenshots/xquery_panel_with_results_new.png")
    
    print("\n✓ Screenshots generated successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
