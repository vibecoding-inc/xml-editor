#!/usr/bin/env python3
"""
Generate screenshots for XQuery panel - minimal approach.
"""
import sys, os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication
from xmleditor.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.resize(1400, 900)

# Manually set XML content instead of using load_file
editor = window.get_current_editor()
if editor:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="web">
        <title lang="en">Learning XML</title>
        <author>Erik T. Ray</author>
        <year>2003</year>
        <price>39.95</price>
    </book>
    <book category="cooking">
        <title lang="en">Everyday Italian</title>
        <author>Giada De Laurentiis</author>
        <year>2005</year>
        <price>30.00</price>
    </book>
</bookstore>"""
    editor.set_text(xml_content)

# Open XQuery panel
window.toggle_xquery_panel()

# Set query content directly
window.xquery_panel.xquery_editor.set_text("(: Get all book titles where price > 30 :)\n//book[price > 30]/title/text()")
window.xquery_panel.xquery_file_path = "/tmp/sample.xq"
window.xquery_panel.file_path_display.setText("/tmp/sample.xq")

# Screenshot before execution
os.makedirs("screenshots", exist_ok=True)
pixmap = window.grab()
pixmap.save("screenshots/xquery_panel_new_ui.png")
print("✓ Saved: screenshots/xquery_panel_new_ui.png")

# Execute query
window.xquery_panel.execute_query()

# Screenshot after execution
pixmap = window.grab()
pixmap.save("screenshots/xquery_panel_with_results_new.png")
print("✓ Saved: screenshots/xquery_panel_with_results_new.png")

print("\n✓ Done!")
sys.exit(0)
