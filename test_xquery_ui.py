#!/usr/bin/env python3
"""Quick test of XQuery panel UI"""
import sys
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from xmleditor.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.resize(1400, 900)
window.show()

# Load XML
window.load_file("/tmp/xquery_test/sample.xml")

# Open XQuery panel
window.toggle_xquery_panel()

# Load query
window.xquery_panel.load_file("/tmp/xquery_test/sample.xq")

# Take screenshot before
pixmap = window.grab()
os.makedirs("screenshots", exist_ok=True)
pixmap.save("screenshots/xquery_panel_new_ui_before.png")
print("Saved: screenshots/xquery_panel_new_ui_before.png")

# Execute query
window.xquery_panel.execute_query()

# Take screenshot after
pixmap = window.grab()
pixmap.save("screenshots/xquery_panel_new_ui_after.png")
print("Saved: screenshots/xquery_panel_new_ui_after.png")

print("Done!")
sys.exit(0)
