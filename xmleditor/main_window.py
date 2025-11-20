"""
Main window for the XML Editor application.
"""

import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QSplitter, QMenuBar, QMenu, QToolBar, QFileDialog, 
                              QMessageBox, QInputDialog, QDockWidget, QTextEdit,
                              QLabel, QStatusBar)
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QActionGroup
from PyQt6.QtCore import Qt, QSettings
from PyQt6.Qsci import QsciScintilla
from xmleditor.xml_editor import XMLEditor
from xmleditor.xml_tree_view import XMLTreeView
from xmleditor.xpath_dialog import XPathDialog
from xmleditor.validation_dialog import ValidationDialog
from xmleditor.xslt_dialog import XSLTDialog
from xmleditor.xml_utils import XMLUtilities
from xmleditor.theme_manager import ThemeManager, ThemeType


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.is_modified = False
        self.settings = QSettings("XMLEditor", "XMLEditor")
        self.recent_files = self.load_recent_files()
        
        # Load theme preference
        theme_name = self.settings.value("theme", ThemeType.SYSTEM.value)
        try:
            self.current_theme = ThemeType(theme_name)
        except ValueError:
            self.current_theme = ThemeType.SYSTEM
        
        self.init_ui()
        self.create_new_document()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("XML Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for editor and tree view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create editor with theme
        self.editor = XMLEditor(theme_type=self.current_theme)
        self.editor.textChanged.connect(self.on_text_changed)
        splitter.addWidget(self.editor)
        
        # Create tree view
        self.tree_view = XMLTreeView()
        splitter.addWidget(self.tree_view)
        
        # Set splitter sizes (70% editor, 30% tree)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
        
        # Create error/output panel as dock widget
        self.create_output_panel()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.create_status_bar()
        
        # Restore window state
        self.restore_settings()
        
    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Create a new XML document")
        new_action.triggered.connect(self.create_new_document)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open an XML file")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_files_menu()
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip("Save the current document")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip("Save the current document with a new name")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Find...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)
        
        replace_action = QAction("&Replace...", self)
        replace_action.setShortcut(QKeySequence.StandardKey.Replace)
        replace_action.triggered.connect(self.replace_text)
        edit_menu.addAction(replace_action)
        
        edit_menu.addSeparator()
        
        comment_action = QAction("Comment/&Uncomment", self)
        comment_action.setShortcut(QKeySequence("Ctrl+/"))
        comment_action.triggered.connect(self.toggle_comment)
        edit_menu.addAction(comment_action)
        
        # XML menu
        xml_menu = menubar.addMenu("&XML")
        
        format_action = QAction("&Format XML", self)
        format_action.setShortcut(QKeySequence("Ctrl+Shift+F"))
        format_action.setStatusTip("Format and indent XML")
        format_action.triggered.connect(self.format_xml)
        xml_menu.addAction(format_action)
        
        validate_action = QAction("&Validate...", self)
        validate_action.setShortcut(QKeySequence("Ctrl+Shift+V"))
        validate_action.setStatusTip("Validate XML")
        validate_action.triggered.connect(self.validate_xml)
        xml_menu.addAction(validate_action)
        
        xml_menu.addSeparator()
        
        xpath_action = QAction("&XPath Query...", self)
        xpath_action.setShortcut(QKeySequence("Ctrl+Shift+X"))
        xpath_action.setStatusTip("Execute XPath query")
        xpath_action.triggered.connect(self.show_xpath_dialog)
        xml_menu.addAction(xpath_action)
        
        xslt_action = QAction("XS&LT Transform...", self)
        xslt_action.setShortcut(QKeySequence("Ctrl+Shift+T"))
        xslt_action.setStatusTip("Apply XSLT transformation")
        xslt_action.triggered.connect(self.show_xslt_dialog)
        xml_menu.addAction(xslt_action)
        
        xml_menu.addSeparator()
        
        refresh_tree_action = QAction("Refresh &Tree View", self)
        refresh_tree_action.setShortcut(QKeySequence("F5"))
        refresh_tree_action.setStatusTip("Refresh XML tree view")
        refresh_tree_action.triggered.connect(self.refresh_tree_view)
        xml_menu.addAction(refresh_tree_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        toggle_tree_action = QAction("Toggle Tree &View", self)
        toggle_tree_action.setShortcut(QKeySequence("Ctrl+T"))
        toggle_tree_action.triggered.connect(self.toggle_tree_view)
        view_menu.addAction(toggle_tree_action)
        
        toggle_output_action = QAction("Toggle &Output Panel", self)
        toggle_output_action.setShortcut(QKeySequence("Ctrl+O"))
        toggle_output_action.triggered.connect(self.toggle_output_panel)
        view_menu.addAction(toggle_output_action)
        
        view_menu.addSeparator()
        
        word_wrap_action = QAction("Word &Wrap", self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        view_menu.addAction(word_wrap_action)
        
        view_menu.addSeparator()
        
        # Theme submenu
        theme_menu = view_menu.addMenu("&Theme")
        theme_action_group = QActionGroup(self)
        theme_action_group.setExclusive(True)
        
        theme_names = ThemeManager.get_theme_names()
        for theme_type, theme_name in theme_names.items():
            action = QAction(theme_name, self)
            action.setCheckable(True)
            action.setData(theme_type)
            if theme_type == self.current_theme:
                action.setChecked(True)
            action.triggered.connect(lambda checked, t=theme_type: self.change_theme(t))
            theme_action_group.addAction(action)
            theme_menu.addAction(action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("About XML Editor")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # File actions
        new_action = QAction("New", self)
        new_action.triggered.connect(self.create_new_document)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Edit actions
        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.editor.undo)
        toolbar.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.editor.redo)
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()
        
        # XML actions
        format_action = QAction("Format", self)
        format_action.triggered.connect(self.format_xml)
        toolbar.addAction(format_action)
        
        validate_action = QAction("Validate", self)
        validate_action.triggered.connect(self.validate_xml)
        toolbar.addAction(validate_action)
        
        xpath_action = QAction("XPath", self)
        xpath_action.triggered.connect(self.show_xpath_dialog)
        toolbar.addAction(xpath_action)
        
    def create_status_bar(self):
        """Create status bar."""
        self.statusBar().showMessage("Ready")
        
    def create_output_panel(self):
        """Create output/error panel."""
        self.output_dock = QDockWidget("Output", self)
        self.output_panel = QTextEdit()
        self.output_panel.setReadOnly(True)
        self.output_panel.setMaximumHeight(150)
        self.output_dock.setWidget(self.output_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.output_dock)
        self.output_dock.hide()
        
    def create_new_document(self):
        """Create a new XML document."""
        if self.check_save_changes():
            self.editor.clear_content()
            self.editor.set_text('<?xml version="1.0" encoding="UTF-8"?>\n<root>\n    \n</root>')
            self.current_file = None
            self.is_modified = False
            self.update_window_title()
            self.tree_view.clear()
            
    def open_file(self):
        """Open an XML file."""
        if not self.check_save_changes():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open XML File", "", "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path):
        """Load file from path."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.editor.set_text(content)
            self.current_file = file_path
            self.is_modified = False
            self.update_window_title()
            self.add_recent_file(file_path)
            self.refresh_tree_view()
            self.output_panel.clear()
            self.statusBar().showMessage(f"Opened: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")
            
    def save_file(self):
        """Save the current file."""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Save the current file with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save XML File", "", "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            self.save_to_file(file_path)
            
    def save_to_file(self, file_path):
        """Save content to file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.get_text())
            
            self.current_file = file_path
            self.is_modified = False
            self.update_window_title()
            self.add_recent_file(file_path)
            self.statusBar().showMessage(f"Saved: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
            
    def format_xml(self):
        """Format the XML content."""
        content = self.editor.get_text().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "No content to format")
            return
        
        try:
            formatted = XMLUtilities.format_xml(content)
            self.editor.set_text(formatted)
            self.statusBar().showMessage("XML formatted successfully")
            self.refresh_tree_view()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to format XML:\n{str(e)}")
            self.output_panel.setPlainText(f"Format Error:\n{str(e)}")
            self.output_dock.show()
            
    def validate_xml(self):
        """Open validation dialog."""
        content = self.editor.get_text().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "No content to validate")
            return
        
        dialog = ValidationDialog(content, self)
        dialog.exec()
        
    def show_xpath_dialog(self):
        """Open XPath query dialog."""
        content = self.editor.get_text().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "No content to query")
            return
        
        dialog = XPathDialog(content, self)
        dialog.exec()
        
    def show_xslt_dialog(self):
        """Open XSLT transformation dialog."""
        content = self.editor.get_text().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "No content to transform")
            return
        
        dialog = XSLTDialog(content, self)
        if dialog.exec():
            transformed = dialog.get_transformed_xml()
            if transformed:
                self.editor.set_text(transformed)
                self.refresh_tree_view()
                
    def refresh_tree_view(self):
        """Refresh the XML tree view."""
        content = self.editor.get_text().strip()
        
        if content:
            try:
                self.tree_view.load_xml(content)
                self.output_panel.clear()
                self.output_dock.hide()
            except Exception as e:
                self.output_panel.setPlainText(f"Error refreshing tree:\n{str(e)}")
                self.output_dock.show()
        else:
            self.tree_view.clear()
            
    def find_text(self):
        """Find text in editor."""
        text, ok = QInputDialog.getText(self, "Find", "Find text:")
        if ok and text:
            if not self.editor.findFirst(text, False, True, False, True):
                QMessageBox.information(self, "Find", f"'{text}' not found")
                
    def replace_text(self):
        """Replace text in editor."""
        find_text, ok = QInputDialog.getText(self, "Replace", "Find text:")
        if not ok or not find_text:
            return
        
        replace_text, ok = QInputDialog.getText(self, "Replace", "Replace with:")
        if not ok:
            return
        
        content = self.editor.get_text()
        new_content = content.replace(find_text, replace_text)
        
        if content != new_content:
            self.editor.set_text(new_content)
            count = content.count(find_text)
            QMessageBox.information(self, "Replace", f"Replaced {count} occurrence(s)")
        else:
            QMessageBox.information(self, "Replace", f"'{find_text}' not found")
            
    def toggle_comment(self):
        """Toggle XML comment for selected text."""
        # Get selected text
        if self.editor.hasSelectedText():
            start_line, start_pos, end_line, end_pos = self.editor.getSelection()
            selected_text = self.editor.selectedText()
            
            # Check if already commented
            if selected_text.strip().startswith('<!--') and selected_text.strip().endswith('-->'):
                # Uncomment
                new_text = selected_text.replace('<!--', '', 1).rsplit('-->', 1)[0]
                self.editor.replaceSelectedText(new_text)
            else:
                # Comment
                new_text = f"<!-- {selected_text} -->"
                self.editor.replaceSelectedText(new_text)
        else:
            # Comment current line
            line, pos = self.editor.getCursorPosition()
            line_text = self.editor.text(line)
            
            if '<!--' in line_text and '-->' in line_text:
                # Uncomment
                new_text = line_text.replace('<!--', '').replace('-->', '')
            else:
                # Comment
                new_text = f"<!-- {line_text.strip()} -->"
            
            self.editor.setSelection(line, 0, line, len(line_text))
            self.editor.replaceSelectedText(new_text)
            
    def toggle_tree_view(self):
        """Toggle tree view visibility."""
        if self.tree_view.isVisible():
            self.tree_view.hide()
        else:
            self.tree_view.show()
            self.refresh_tree_view()
            
    def toggle_output_panel(self):
        """Toggle output panel visibility."""
        if self.output_dock.isVisible():
            self.output_dock.hide()
        else:
            self.output_dock.show()
            
    def toggle_word_wrap(self, checked):
        """Toggle word wrap in editor."""
        if checked:
            self.editor.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        else:
            self.editor.setWrapMode(QsciScintilla.WrapMode.WrapNone)
    
    def change_theme(self, theme_type):
        """Change the editor theme."""
        self.current_theme = theme_type
        self.editor.apply_theme(theme_type)
        self.settings.setValue("theme", theme_type.value)
        self.statusBar().showMessage(f"Theme changed to {ThemeManager.get_theme_names()[theme_type]}")
            
    def on_text_changed(self):
        """Handle text changed event."""
        self.is_modified = True
        self.update_window_title()
        
    def update_window_title(self):
        """Update window title based on current file and modified state."""
        title = "XML Editor"
        
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        else:
            title += " - Untitled"
        
        if self.is_modified:
            title += " *"
        
        self.setWindowTitle(title)
        
    def check_save_changes(self):
        """Check if there are unsaved changes and prompt user."""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Do you want to save your changes?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.StandardButton.Discard:
                return True
            else:
                return False
        
        return True
        
    def closeEvent(self, event):
        """Handle window close event."""
        if self.check_save_changes():
            self.save_settings()
            event.accept()
        else:
            event.ignore()
            
    def load_recent_files(self):
        """Load recent files list."""
        return self.settings.value("recent_files", [])
        
    def save_recent_files(self):
        """Save recent files list."""
        self.settings.setValue("recent_files", self.recent_files)
        
    def add_recent_file(self, file_path):
        """Add file to recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        self.save_recent_files()
        self.update_recent_files_menu()
        
    def update_recent_files_menu(self):
        """Update recent files menu."""
        self.recent_menu.clear()
        
        for file_path in self.recent_files:
            if os.path.exists(file_path):
                action = QAction(os.path.basename(file_path), self)
                action.setStatusTip(file_path)
                action.triggered.connect(lambda checked, path=file_path: self.load_file(path))
                self.recent_menu.addAction(action)
        
        if not self.recent_files:
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
            
    def restore_settings(self):
        """Restore window settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
            
    def save_settings(self):
        """Save window settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>XML Editor</h2>
        <p>Version 1.0.0</p>
        <p>A fully-featured cross-platform XML editor with:</p>
        <ul>
            <li>XML syntax highlighting</li>
            <li>XPath query support</li>
            <li>XML Schema (XSD) validation</li>
            <li>DTD validation</li>
            <li>XSLT transformation</li>
            <li>XML tree view</li>
            <li>XML formatting</li>
            <li>Find and replace</li>
            <li>Recent files</li>
        </ul>
        <p>Built with Python and PyQt6</p>
        """
        QMessageBox.about(self, "About XML Editor", about_text)
