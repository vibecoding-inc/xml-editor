"""
Main window for the XML Editor application.
"""

import os
import html
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QSplitter, QMenuBar, QMenu, QToolBar, QFileDialog, 
                              QMessageBox, QInputDialog, QDockWidget, QTextEdit,
                              QLabel, QStatusBar, QTabWidget, QPushButton, QTabBar,
                              QComboBox, QCheckBox, QFrame, QTextBrowser)
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QActionGroup
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.Qsci import QsciScintilla
from xmleditor.xml_editor import XMLEditor
from xmleditor.xml_tree_view import XMLTreeView
from xmleditor.xml_graph_view import XMLGraphView
from xmleditor.xpath_dialog import XPathDialog
from xmleditor.validation_dialog import ValidationDialog
from xmleditor.xslt_dialog import XSLTDialog
from xmleditor.schema_generation_dialog import SchemaGenerationDialog
from xmleditor.xquery_panel import XQueryPanel
from xmleditor.xml_utils import XMLUtilities
from xmleditor.theme_manager import ThemeManager, ThemeType


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("XMLEditor", "XMLEditor")
        self.recent_files = self.load_recent_files()
        
        # Load theme preference
        theme_name = self.settings.value("theme", ThemeType.SYSTEM.value)
        try:
            self.current_theme = ThemeType(theme_name)
        except ValueError:
            self.current_theme = ThemeType.SYSTEM
        
        # Load namespace display preference
        self.show_namespaces = self.settings.value("show_namespaces", False, type=bool)
            
        # Create timer for auto-refreshing tree view
        self.tree_refresh_timer = QTimer()
        self.tree_refresh_timer.setSingleShot(True)
        self.tree_refresh_timer.timeout.connect(self.auto_refresh_tree_view)
        
        # Create timer for auto-save
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.perform_auto_save)
        self.auto_save_enabled = self.settings.value("auto_save_enabled", False, type=bool)
        self.auto_save_interval = self.settings.value("auto_save_interval", 30, type=int)  # seconds
        
        self.tab_data = {}  # Map tab index to {file_path, is_modified} for primary tabs
        self.split_tab_data = {}  # Same mapping for split-view tabs
        self.editor_tab_map = {}  # Map editor widgets to their parent tab widget
        self.last_active_editor = None
        self.init_ui()
        self.create_new_document()
        
        # Start auto-save timer if enabled
        if self.auto_save_enabled:
            self.auto_save_timer.start(self.auto_save_interval * 1000)  # Convert to milliseconds
        
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
        
        # Create tab widget for multiple editors (primary)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(lambda idx: self.close_tab(idx, self.tab_widget))
        self.tab_widget.currentChanged.connect(lambda idx: self.on_tab_changed(idx, self.tab_widget))

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.tab_widget)
        
        # Create tree view
        self.tree_view = XMLTreeView()
        splitter.addWidget(self.tree_view)
        
        # Set splitter sizes (70% editor, 30% tree)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
        
        # Create split-view dock (can be floated to another monitor)
        self.split_tab_widget = QTabWidget()
        self.split_tab_widget.setTabsClosable(True)
        self.split_tab_widget.setMovable(True)
        self.split_tab_widget.tabCloseRequested.connect(lambda idx: self.close_tab(idx, self.split_tab_widget))
        self.split_tab_widget.currentChanged.connect(lambda idx: self.on_tab_changed(idx, self.split_tab_widget))
        
        self.split_dock = QDockWidget("Split View", self)
        self.split_dock.setObjectName("SplitViewDock")
        self.split_dock.setWidget(self.split_tab_widget)
        self.split_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.split_dock)
        self.split_dock.hide()
        
        # Create error/output panel as dock widget
        self.create_output_panel()
        
        # Create validation panel as dock widget
        self.create_validation_panel()
        
        # Create graph view panel as dock widget
        self.create_graph_panel()
        
        # Create XSLT panel as dock widget
        self.create_xslt_panel()
        
        # Create XQuery panel as dock widget
        self.create_xquery_panel()
        
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
        
        # Auto-save checkbox
        self.auto_save_action = QAction("Auto Save", self)
        self.auto_save_action.setCheckable(True)
        self.auto_save_action.setChecked(self.auto_save_enabled)
        self.auto_save_action.setStatusTip("Automatically save files every 30 seconds")
        self.auto_save_action.triggered.connect(self.toggle_auto_save)
        file_menu.addAction(self.auto_save_action)
        
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
        undo_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().undo())
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().redo())
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().cut())
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().copy())
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().paste())
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
        
        generate_schema_action = QAction("&Generate Schema...", self)
        generate_schema_action.setShortcut(QKeySequence("Ctrl+Shift+G"))
        generate_schema_action.setStatusTip("Generate XSD or DTD schema from XML")
        generate_schema_action.triggered.connect(self.show_schema_generation_dialog)
        xml_menu.addAction(generate_schema_action)
        
        xml_menu.addSeparator()
        
        xpath_action = QAction("&XPath Query...", self)
        xpath_action.setShortcut(QKeySequence("Ctrl+Shift+X"))
        xpath_action.setStatusTip("Execute XPath query")
        xpath_action.triggered.connect(self.show_xpath_dialog)
        xml_menu.addAction(xpath_action)
        
        xquery_action = QAction("X&Query...", self)
        xquery_action.setShortcut(QKeySequence("Ctrl+Shift+Q"))
        xquery_action.setStatusTip("Execute XQuery expressions")
        xquery_action.triggered.connect(self.toggle_xquery_panel)
        xml_menu.addAction(xquery_action)
        
        xslt_action = QAction("XS&LT Transform...", self)
        xslt_action.setShortcut(QKeySequence("Ctrl+Shift+T"))
        xslt_action.setStatusTip("Apply XSLT transformation")
        xslt_action.triggered.connect(self.toggle_xslt_panel)
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
        
        toggle_validation_action = QAction("Toggle &Validation Panel", self)
        toggle_validation_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
        toggle_validation_action.triggered.connect(self.toggle_validation_panel)
        view_menu.addAction(toggle_validation_action)
        
        toggle_graph_action = QAction("Toggle &Graph View", self)
        toggle_graph_action.setShortcut(QKeySequence("Ctrl+G"))
        toggle_graph_action.setStatusTip("Toggle XML node graph visualization")
        toggle_graph_action.triggered.connect(self.toggle_graph_panel)
        view_menu.addAction(toggle_graph_action)
        
        toggle_xslt_action = QAction("Toggle XS&LT Panel", self)
        toggle_xslt_action.setShortcut(QKeySequence("Ctrl+L"))
        toggle_xslt_action.setStatusTip("Toggle XSLT transformation panel")
        toggle_xslt_action.triggered.connect(self.toggle_xslt_panel)
        view_menu.addAction(toggle_xslt_action)
        
        toggle_xquery_action = QAction("Toggle X&Query Panel", self)
        toggle_xquery_action.setStatusTip("Toggle XQuery execution panel")
        toggle_xquery_action.triggered.connect(self.toggle_xquery_panel)
        view_menu.addAction(toggle_xquery_action)
        
        view_menu.addSeparator()
        
        self.toggle_split_view_action = QAction("Toggle Split View", self)
        self.toggle_split_view_action.setCheckable(True)
        self.toggle_split_view_action.triggered.connect(self.toggle_split_view)
        view_menu.addAction(self.toggle_split_view_action)
        self.split_dock.visibilityChanged.connect(lambda visible: self.toggle_split_view_action.setChecked(visible))
        self.toggle_split_view_action.setChecked(self.split_dock.isVisible())
        
        move_to_split_action = QAction("Move Tab to Split View", self)
        move_to_split_action.setShortcut(QKeySequence("Ctrl+\\"))
        move_to_split_action.triggered.connect(self.move_tab_to_split_view)
        view_menu.addAction(move_to_split_action)
        
        view_menu.addSeparator()
        
        word_wrap_action = QAction("Word &Wrap", self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        view_menu.addAction(word_wrap_action)
        
        show_namespaces_action = QAction("Show &Namespaces in Tree", self)
        show_namespaces_action.setCheckable(True)
        show_namespaces_action.setChecked(self.show_namespaces)
        show_namespaces_action.triggered.connect(self.toggle_show_namespaces)
        view_menu.addAction(show_namespaces_action)
        
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
        toolbar.setObjectName("MainToolbar")
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
        undo_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().undo())
        toolbar.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().redo())
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
        
        xquery_action = QAction("XQuery", self)
        xquery_action.triggered.connect(self.toggle_xquery_panel)
        toolbar.addAction(xquery_action)
        
        toolbar.addSeparator()
        
        graph_action = QAction("Graph", self)
        graph_action.setStatusTip("Toggle XML node graph visualization")
        graph_action.triggered.connect(self.toggle_graph_panel)
        toolbar.addAction(graph_action)
        
    def create_status_bar(self):
        """Create status bar."""
        status_bar = self.statusBar()
        status_bar.showMessage("Ready")
        self.active_view_label = QLabel("")
        status_bar.addPermanentWidget(self.active_view_label)
        
    def create_output_panel(self):
        """Create output/error panel."""
        self.output_dock = QDockWidget("Output", self)
        self.output_dock.setObjectName("OutputDock")
        self.output_panel = QTextEdit()
        self.output_panel.setReadOnly(True)
        self.output_panel.setMaximumHeight(150)
        self.output_dock.setWidget(self.output_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.output_dock)
        self.output_dock.hide()
        
    def create_validation_panel(self):
        """Create persistent validation panel."""
        self.validation_dock = QDockWidget("Validation", self)
        self.validation_dock.setObjectName("ValidationDock")
        validation_widget = QWidget()
        validation_layout = QVBoxLayout(validation_widget)
        
        # Validation type selector and buttons
        button_layout = QHBoxLayout()
        
        self.validate_well_formed_btn = QPushButton("Well-Formed")
        self.validate_well_formed_btn.clicked.connect(self.validate_well_formed)
        button_layout.addWidget(self.validate_well_formed_btn)
        
        self.validate_xsd_btn = QPushButton("Validate XSD")
        self.validate_xsd_btn.clicked.connect(self.validate_with_xsd)
        button_layout.addWidget(self.validate_xsd_btn)
        
        self.validate_dtd_btn = QPushButton("Validate DTD")
        self.validate_dtd_btn.clicked.connect(self.validate_with_dtd)
        button_layout.addWidget(self.validate_dtd_btn)
        
        button_layout.addStretch()
        validation_layout.addLayout(button_layout)
        
        # Schema input area with tabs
        schema_label = QLabel("Schema/DTD Source:")
        validation_layout.addWidget(schema_label)
        
        # Create tab widget for schema input methods
        self.schema_input_tabs = QTabWidget()
        
        # Tab 1: Text input
        text_input_widget = QWidget()
        text_input_layout = QVBoxLayout(text_input_widget)
        
        self.validation_schema_input = QTextEdit()
        self.validation_schema_input.setPlaceholderText("Paste XSD schema or DTD here...")
        self.validation_schema_input.setMaximumHeight(120)
        text_input_layout.addWidget(self.validation_schema_input)
        
        text_file_layout = QHBoxLayout()
        load_schema_btn = QPushButton("Load from File")
        load_schema_btn.clicked.connect(self.load_schema_file)
        text_file_layout.addWidget(load_schema_btn)
        text_file_layout.addStretch()
        text_input_layout.addLayout(text_file_layout)
        
        self.schema_input_tabs.addTab(text_input_widget, "Text Input")
        
        # Tab 2: File picker
        file_picker_widget = QWidget()
        file_picker_layout = QVBoxLayout(file_picker_widget)
        
        # File path display and picker
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(QLabel("Schema File:"))
        
        self.schema_file_path_label = QLabel("No file selected")
        self.schema_file_path_label.setStyleSheet("color: gray; font-style: italic;")
        file_path_layout.addWidget(self.schema_file_path_label, 1)
        
        select_file_btn = QPushButton("Browse...")
        select_file_btn.clicked.connect(self.select_schema_file)
        file_path_layout.addWidget(select_file_btn)
        
        clear_file_btn = QPushButton("Clear")
        clear_file_btn.clicked.connect(self.clear_schema_file)
        file_path_layout.addWidget(clear_file_btn)
        
        file_picker_layout.addLayout(file_path_layout)
        
        # Info label
        info_label = QLabel("The schema file will be reloaded from disk each time validation is performed.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        file_picker_layout.addWidget(info_label)
        
        file_picker_layout.addStretch()
        
        self.schema_input_tabs.addTab(file_picker_widget, "File Path")
        
        validation_layout.addWidget(self.schema_input_tabs)
        
        # Store schema file path
        self.schema_file_path = None
        
        # Validation result area
        result_label = QLabel("Validation Result:")
        validation_layout.addWidget(result_label)
        
        self.validation_result = QTextEdit()
        self.validation_result.setReadOnly(True)
        validation_layout.addWidget(self.validation_result)
        
        self.validation_dock.setWidget(validation_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.validation_dock)
        self.validation_dock.hide()
    
    def create_graph_panel(self):
        """Create XML graph visualization panel."""
        self.graph_dock = QDockWidget("XML Graph View", self)
        self.graph_dock.setObjectName("GraphDock")
        
        # Create container widget with layout
        graph_widget = QWidget()
        graph_layout = QVBoxLayout(graph_widget)
        graph_layout.setContentsMargins(5, 2, 5, 2)
        graph_layout.setSpacing(2)
        
        # Single compact toolbar row with all controls
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(5)
        
        # Refresh and Fit buttons
        refresh_btn = QPushButton("⟳")
        refresh_btn.setToolTip("Refresh graph")
        refresh_btn.setMaximumWidth(30)
        refresh_btn.clicked.connect(self.refresh_graph_view)
        toolbar_layout.addWidget(refresh_btn)
        
        fit_btn = QPushButton("⊡")
        fit_btn.setToolTip("Fit to view")
        fit_btn.setMaximumWidth(30)
        fit_btn.clicked.connect(self.fit_graph_to_view)
        toolbar_layout.addWidget(fit_btn)
        
        toolbar_layout.addWidget(self._create_separator())
        
        # Layout algorithm selector
        layout_label = QLabel("Layout:")
        layout_label.setStyleSheet("font-size: 10px;")
        toolbar_layout.addWidget(layout_label)
        
        self.graph_layout_combo = QComboBox()
        self.graph_layout_combo.addItems(["Tree (Top-Down)", "Tree (Left-Right)", "Radial", "Compact"])
        self.graph_layout_combo.setMaximumWidth(120)
        self.graph_layout_combo.setToolTip("Select layout algorithm")
        self.graph_layout_combo.currentIndexChanged.connect(self.on_graph_layout_changed)
        toolbar_layout.addWidget(self.graph_layout_combo)
        
        toolbar_layout.addWidget(self._create_separator())
        
        # View mode toggle (Data vs Types)
        view_mode_label = QLabel("View:")
        view_mode_label.setStyleSheet("font-size: 10px;")
        toolbar_layout.addWidget(view_mode_label)
        
        self.graph_view_mode_combo = QComboBox()
        self.graph_view_mode_combo.addItems(["Data", "Types"])
        self.graph_view_mode_combo.setMaximumWidth(70)
        self.graph_view_mode_combo.setToolTip("Data: show all XML elements\nTypes: show unique element types (schema-like)")
        self.graph_view_mode_combo.currentIndexChanged.connect(self.on_graph_view_mode_changed)
        toolbar_layout.addWidget(self.graph_view_mode_combo)
        
        toolbar_layout.addWidget(self._create_separator())
        
        # Display checkboxes
        self.show_connections_cb = QCheckBox("Lines")
        self.show_connections_cb.setChecked(True)
        self.show_connections_cb.setToolTip("Show connection lines")
        self.show_connections_cb.stateChanged.connect(self.on_graph_display_changed)
        toolbar_layout.addWidget(self.show_connections_cb)
        
        self.show_nesting_cb = QCheckBox("Nesting")
        self.show_nesting_cb.setChecked(True)
        self.show_nesting_cb.setToolTip("Show nesting containers")
        self.show_nesting_cb.stateChanged.connect(self.on_graph_display_changed)
        toolbar_layout.addWidget(self.show_nesting_cb)
        
        self.show_keyrefs_cb = QCheckBox("Key Refs")
        self.show_keyrefs_cb.setChecked(True)
        self.show_keyrefs_cb.setToolTip("Show key reference lines")
        self.show_keyrefs_cb.stateChanged.connect(self.on_graph_display_changed)
        toolbar_layout.addWidget(self.show_keyrefs_cb)
        
        toolbar_layout.addWidget(self._create_separator())
        
        # Schema controls
        self.graph_schema_path_label = QLabel("No schema")
        self.graph_schema_path_label.setStyleSheet("color: gray; font-size: 9px;")
        self.graph_schema_path_label.setMaximumWidth(80)
        toolbar_layout.addWidget(self.graph_schema_path_label)
        
        load_schema_btn = QPushButton("📂")
        load_schema_btn.setToolTip("Load XSD schema for key references")
        load_schema_btn.setMaximumWidth(30)
        load_schema_btn.clicked.connect(self.load_graph_schema)
        toolbar_layout.addWidget(load_schema_btn)
        
        clear_schema_btn = QPushButton("✕")
        clear_schema_btn.setToolTip("Clear schema")
        clear_schema_btn.setMaximumWidth(25)
        clear_schema_btn.clicked.connect(self.clear_graph_schema)
        toolbar_layout.addWidget(clear_schema_btn)
        
        toolbar_layout.addStretch()
        graph_layout.addLayout(toolbar_layout)
        
        # Store schema file path and content
        self.graph_schema_file_path = None
        self.graph_schema_content = None
        
        # Create graph view
        self.graph_view = XMLGraphView()
        graph_layout.addWidget(self.graph_view)
        
        self.graph_dock.setWidget(graph_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.graph_dock)
        self.graph_dock.hide()
    
    def create_xslt_panel(self):
        """Create XSLT transformation panel."""
        self.xslt_dock = QDockWidget("XSLT Transform", self)
        self.xslt_dock.setObjectName("XSLTDock")
        xslt_widget = QWidget()
        xslt_layout = QVBoxLayout(xslt_widget)
        
        # XSLT stylesheet input area with tabs
        stylesheet_label = QLabel("XSLT Stylesheet:")
        xslt_layout.addWidget(stylesheet_label)
        
        # Create tab widget for XSLT input methods
        self.xslt_input_tabs = QTabWidget()
        
        # Tab indices for input tabs
        self.XSLT_TEXT_INPUT_TAB = 0
        self.XSLT_FILE_PATH_TAB = 1
        
        # Tab 1: Text input
        text_input_widget = QWidget()
        text_input_layout = QVBoxLayout(text_input_widget)
        
        self.xslt_text_input = QTextEdit()
        self.xslt_text_input.setPlaceholderText("Paste XSLT stylesheet here...")
        self.xslt_text_input.setMaximumHeight(150)
        text_input_layout.addWidget(self.xslt_text_input)
        
        text_file_layout = QHBoxLayout()
        load_xslt_btn = QPushButton("Load from File")
        load_xslt_btn.clicked.connect(self.load_xslt_text_file)
        text_file_layout.addWidget(load_xslt_btn)
        text_file_layout.addStretch()
        text_input_layout.addLayout(text_file_layout)
        
        self.xslt_input_tabs.addTab(text_input_widget, "Text Input")
        
        # Tab 2: File picker
        file_picker_widget = QWidget()
        file_picker_layout = QVBoxLayout(file_picker_widget)
        
        # File path display and picker
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(QLabel("XSLT File:"))
        
        self.xslt_file_path_label = QLabel("No file selected")
        self.xslt_file_path_label.setStyleSheet("color: gray; font-style: italic;")
        file_path_layout.addWidget(self.xslt_file_path_label, 1)
        
        select_xslt_file_btn = QPushButton("Browse...")
        select_xslt_file_btn.clicked.connect(self.select_xslt_file)
        file_path_layout.addWidget(select_xslt_file_btn)
        
        clear_xslt_file_btn = QPushButton("Clear")
        clear_xslt_file_btn.clicked.connect(self.clear_xslt_file)
        file_path_layout.addWidget(clear_xslt_file_btn)
        
        file_picker_layout.addLayout(file_path_layout)
        
        # Info label
        info_label = QLabel("The XSLT file will be reloaded from disk each time transformation is performed.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        file_picker_layout.addWidget(info_label)
        
        file_picker_layout.addStretch()
        
        self.xslt_input_tabs.addTab(file_picker_widget, "File Path")
        
        xslt_layout.addWidget(self.xslt_input_tabs)
        
        # Store XSLT file path
        self.xslt_file_path = None
        
        # Transform button
        transform_btn = QPushButton("Transform")
        transform_btn.clicked.connect(self.apply_xslt_transformation)
        xslt_layout.addWidget(transform_btn)
        
        # Result display area with tabs
        result_label = QLabel("Transformation Result:")
        xslt_layout.addWidget(result_label)
        
        # Create tab widget for result display
        self.xslt_result_tabs = QTabWidget()
        
        # Tab indices for result tabs
        self.XSLT_XML_OUTPUT_TAB = 0
        self.XSLT_HTML_PREVIEW_TAB = 1
        
        # Tab 1: XML/Text output with syntax highlighting
        self.xslt_result_editor = XMLEditor(theme_type=self.current_theme)
        self.xslt_result_editor.setReadOnly(True)
        self.xslt_result_tabs.addTab(self.xslt_result_editor, "XML Output")
        
        # Tab 2: HTML preview
        self.xslt_result_browser = QTextBrowser()
        # Disable link activation for security (QTextBrowser doesn't support JavaScript)
        self.xslt_result_browser.setOpenLinks(False)
        self.xslt_result_tabs.addTab(self.xslt_result_browser, "HTML Preview")
        
        xslt_layout.addWidget(self.xslt_result_tabs)
        
        self.xslt_dock.setWidget(xslt_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.xslt_dock)
        self.xslt_dock.hide()
    
    def create_xquery_panel(self):
        """Create XQuery execution panel."""
        self.xquery_dock = QDockWidget("XQuery", self)
        self.xquery_dock.setObjectName("XQueryDock")
        
        # Create XQuery panel with callback to get current XML
        self.xquery_panel = XQueryPanel(
            theme_type=self.current_theme,
            get_xml_callback=self.get_current_xml_content
        )
        
        self.xquery_dock.setWidget(self.xquery_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.xquery_dock)
        self.xquery_dock.hide()
    
    def get_current_xml_content(self):
        """Get the XML content from the current editor tab."""
        editor = self.get_current_editor()
        if editor:
            return editor.get_text()
        return None
    
    def _create_separator(self):
        """Create a vertical separator line."""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator
    
    def on_graph_layout_changed(self, index):
        """Handle layout algorithm change."""
        layout_names = ["tree_vertical", "tree_horizontal", "radial", "compact"]
        if index < len(layout_names):
            self.graph_view.set_layout_algorithm(layout_names[index])
            self.refresh_graph_view()
    
    def on_graph_view_mode_changed(self, index):
        """Handle view mode change (Data vs Types)."""
        view_modes = ["data", "types"]
        if index < len(view_modes):
            self.graph_view.set_view_mode(view_modes[index])
            self.refresh_graph_view()
    
    def on_graph_display_changed(self):
        """Handle display option checkbox changes."""
        self.graph_view.set_display_options(
            show_connections=self.show_connections_cb.isChecked(),
            show_nesting=self.show_nesting_cb.isChecked(),
            show_keyrefs=self.show_keyrefs_cb.isChecked()
        )
    
    def load_graph_schema(self):
        """Load XSD schema for key/keyref highlighting in graph view."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Schema for Key References", "", 
            "XSD Schema Files (*.xsd);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.graph_schema_content = f.read()
                
                self.graph_schema_file_path = file_path
                basename = os.path.basename(file_path)
                # Truncate for compact display
                display_name = basename[:10] + "..." if len(basename) > 13 else basename
                self.graph_schema_path_label.setText(display_name)
                self.graph_schema_path_label.setToolTip(file_path)
                self.graph_schema_path_label.setStyleSheet("color: green; font-size: 9px;")
                
                # Update graph view with schema
                self.graph_view.set_schema(self.graph_schema_content)
                self.refresh_graph_view()
                
                self.statusBar().showMessage(f"Schema loaded: {basename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load schema:\n{str(e)}")
    
    def clear_graph_schema(self):
        """Clear the loaded graph schema."""
        self.graph_schema_file_path = None
        self.graph_schema_content = None
        self.graph_schema_path_label.setText("No schema")
        self.graph_schema_path_label.setToolTip("")
        self.graph_schema_path_label.setStyleSheet("color: gray; font-size: 9px;")
        
        # Update graph view without schema
        self.graph_view.set_schema(None)
        self.refresh_graph_view()
        
        self.statusBar().showMessage("Schema cleared")
    
    def get_current_editor(self):
        """Get the currently active editor widget."""
        if self.last_active_editor:
            parent_widget = self.editor_tab_map.get(self.last_active_editor)
            if parent_widget and parent_widget.indexOf(self.last_active_editor) != -1:
                return self.last_active_editor
            self.last_active_editor = None
        # Fallback to primary tab
        primary_editor = self.tab_widget.currentWidget()
        if isinstance(primary_editor, XMLEditor):
            return primary_editor
        # Fallback to split view
        split_editor = self.split_tab_widget.currentWidget()
        if isinstance(split_editor, XMLEditor):
            return split_editor
        return None
    
    def get_current_tab_data(self):
        """Get data for the current tab."""
        tab_widget = self.get_active_tab_widget()
        current_index = tab_widget.currentIndex()
        data_store = self._get_data_store(tab_widget)
        if current_index >= 0 and current_index in data_store:
            return data_store[current_index]
        return None
    
    def set_current_tab_data(self, data):
        """Set data for the current tab."""
        tab_widget = self.get_active_tab_widget()
        current_index = tab_widget.currentIndex()
        data_store = self._get_data_store(tab_widget)
        if current_index >= 0:
            data_store[current_index] = data
    
    def get_active_tab_widget(self):
        """Return the tab widget containing the last-focused editor."""
        if self.last_active_editor:
            tab_widget = self.editor_tab_map.get(self.last_active_editor)
            if tab_widget and tab_widget.indexOf(self.last_active_editor) != -1:
                return tab_widget
            self.last_active_editor = None
        if self.split_tab_widget.count() == 0:
            return self.tab_widget
        if self.tab_widget.count() == 0:
            return self.split_tab_widget
        return self.tab_widget
    
    def _get_data_store(self, tab_widget):
        """Return the appropriate tab data store for the given widget."""
        return self.tab_data if tab_widget is self.tab_widget else self.split_tab_data
    
    def _shift_tab_data_after_removal(self, data_store, removed_index):
        """Reindex tab data after removing a tab."""
        new_tab_data = {}
        for i, data in data_store.items():
            if i < removed_index:
                new_tab_data[i] = data
            elif i > removed_index:
                new_tab_data[i - 1] = data
        return new_tab_data
    
    def _update_split_dock_visibility(self):
        """Hide the split dock when it has no tabs."""
        if self.split_tab_widget.count() == 0:
            self.split_dock.hide()
            self.toggle_split_view_action.setChecked(False)
    
    def on_editor_focused(self, editor):
        """Track the last active editor for tool window actions."""
        self.last_active_editor = editor
        self.update_window_title()
    
    def on_tab_changed(self, index, tab_widget=None):
        """Handle tab change event."""
        tab_widget = tab_widget or self.tab_widget
        if index >= 0:
            widget = tab_widget.widget(index)
            if isinstance(widget, XMLEditor):
                self.last_active_editor = widget
            self.refresh_tree_view()
            self.update_window_title()
            # Refresh graph view if visible
            if self.graph_dock.isVisible():
                self.refresh_graph_view()
    
    def close_tab(self, index, tab_widget=None):
        """Close a tab."""
        tab_widget = tab_widget or self.tab_widget
        if index < 0 or index >= tab_widget.count():
            return
        
        data_store = self._get_data_store(tab_widget)
        # Check if tab has unsaved changes (only prompt if not pristine)
        tab_data = data_store.get(index, {})
        is_pristine = tab_data.get('is_pristine', False)
        is_modified = tab_data.get('is_modified', False)
        
        # Only prompt for save if the tab was actually edited by the user (not pristine)
        if is_modified and not is_pristine:
            file_name = os.path.basename(tab_data.get('file_path') or 'Untitled')
            
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                f"Do you want to save changes to {file_name}?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                current_index = tab_widget.currentIndex()
                tab_widget.setCurrentIndex(index)
                self.last_active_editor = tab_widget.widget(index)
                self.save_file()
                tab_widget.setCurrentIndex(current_index)
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        removed_editor = tab_widget.widget(index)
        
        # Remove tab
        tab_widget.removeTab(index)
        self.editor_tab_map.pop(removed_editor, None)
        if self.last_active_editor is removed_editor:
            self.last_active_editor = None
        
        # Update tab_data dictionary (shift indices)
        new_tab_data = self._shift_tab_data_after_removal(data_store, index)
        if tab_widget is self.tab_widget:
            self.tab_data = new_tab_data
        else:
            self.split_tab_data = new_tab_data
            self._update_split_dock_visibility()
        
        # If no tabs remain in either area, create a new one to keep editor usable
        if self.tab_widget.count() == 0 and self.split_tab_widget.count() == 0:
            self.create_new_document()
    
    def create_editor_tab(self, title="Untitled", content="", file_path=None, tab_widget=None):
        """Create a new editor tab."""
        tab_widget = tab_widget or self.tab_widget
        editor = XMLEditor(theme_type=self.current_theme, focus_callback=self.on_editor_focused)
        editor.textChanged.connect(self.on_text_changed)
        if content:
            editor.set_text(content)
        
        index = tab_widget.addTab(editor, title)
        tab_widget.setCurrentIndex(index)
        self.editor_tab_map[editor] = tab_widget
        
        # Track if this is a pristine untitled tab (never edited by user)
        # Pristine tabs can be closed without prompting and are auto-closed when opening files
        is_pristine = file_path is None
        data_store = self._get_data_store(tab_widget)
        data_store[index] = {
            'file_path': file_path,
            'is_modified': False,
            'is_pristine': is_pristine
        }
        
        self.last_active_editor = editor
        self.update_window_title()
        return editor
        
    def create_new_document(self):
        """Create a new XML document."""
        editor = self.create_editor_tab(
            title="Untitled",
            content='<?xml version="1.0" encoding="UTF-8"?>\n<root>\n    \n</root>'
        )
        self.tree_view.clear()
            
    def open_file(self):
        """Open an XML file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open XML File", "", "XML Files (*.xml *.xsd *.dtd);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path, target_widget=None):
        """Load file from path."""
        target_widget = target_widget or self.get_active_tab_widget()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file is already open in a tab
            for widget, data_store in (
                (self.tab_widget, self.tab_data),
                (self.split_tab_widget, self.split_tab_data)
            ):
                for index in range(widget.count()):
                    tab_data = data_store.get(index, {})
                    if tab_data.get('file_path') == file_path:
                        widget.setCurrentIndex(index)
                        existing_editor = widget.widget(index)
                        if isinstance(existing_editor, XMLEditor):
                            self.last_active_editor = existing_editor
                        QMessageBox.information(self, "File Already Open", 
                                              f"The file {os.path.basename(file_path)} is already open.")
                        return
            
            # Close any pristine untitled tabs before opening the new file
            # Iterate in reverse to avoid index shifting issues
            data_store = self._get_data_store(target_widget)
            for index in range(target_widget.count() - 1, -1, -1):
                tab_data = data_store.get(index, {})
                if tab_data.get('is_pristine', False) and tab_data.get('file_path') is None:
                    target_widget.removeTab(index)
                    # Update tab_data dictionary (shift indices)
                    new_tab_data = {}
                    for i, data in data_store.items():
                        if i < index:
                            new_tab_data[i] = data
                        elif i > index:
                            new_tab_data[i - 1] = data
                    if target_widget is self.tab_widget:
                        self.tab_data = new_tab_data
                    else:
                        self.split_tab_data = new_tab_data
            
            # Create new tab for the file
            self.create_editor_tab(
                title=os.path.basename(file_path),
                content=content,
                file_path=file_path,
                tab_widget=target_widget
            )
            
            self.add_recent_file(file_path)
            self.refresh_tree_view()
            self.output_panel.clear()
            self.statusBar().showMessage(f"Opened: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")
            
    def save_file(self):
        """Save the current file."""
        tab_data = self.get_current_tab_data()
        if tab_data and tab_data.get('file_path'):
            self.save_to_file(tab_data['file_path'])
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Save the current file with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save XML File", "", "XML Files (*.xml);;XSD Files (*.xsd);;DTD Files (*.dtd);;All Files (*)"
        )
        
        if file_path:
            self.save_to_file(file_path)
            
    def save_to_file(self, file_path):
        """Save content to file."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(editor.get_text())
            
            tab_widget = self.get_active_tab_widget()
            current_index = tab_widget.currentIndex()
            data_store = self._get_data_store(tab_widget)
            data_store[current_index] = {
                'file_path': file_path,
                'is_modified': False
            }
            
            # Update tab title
            tab_widget.setTabText(current_index, os.path.basename(file_path))
            
            self.update_window_title()
            self.add_recent_file(file_path)
            self.statusBar().showMessage(f"Saved: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def toggle_auto_save(self, checked):
        """Toggle auto-save feature."""
        self.auto_save_enabled = checked
        self.settings.setValue("auto_save_enabled", checked)
        
        if checked:
            self.auto_save_timer.start(self.auto_save_interval * 1000)
            self.statusBar().showMessage(f"Auto-save enabled (every {self.auto_save_interval} seconds)")
        else:
            self.auto_save_timer.stop()
            self.statusBar().showMessage("Auto-save disabled")
    
    def perform_auto_save(self):
        """Perform auto-save for all modified tabs with file paths."""
        saved_count = 0
        
        for tab_widget, data_store in (
            (self.tab_widget, self.tab_data),
            (self.split_tab_widget, self.split_tab_data)
        ):
            for index in range(tab_widget.count()):
                tab_data = data_store.get(index, {})
                file_path = tab_data.get('file_path')
                is_modified = tab_data.get('is_modified', False)
                
                # Only auto-save files that have a path (not "Untitled" documents) and are modified
                if file_path and is_modified:
                    editor = tab_widget.widget(index)
                    if editor:
                        try:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(editor.get_text())
                            
                            # Mark as not modified after successful save
                            data_store[index]['is_modified'] = False
                            saved_count += 1
                        except Exception as e:
                            # Silently log errors during auto-save to avoid disrupting user
                            print(f"Auto-save failed for {file_path}: {str(e)}")
        
        # Update window title for current tab
        if saved_count > 0:
            self.update_window_title()
            # Show brief status message
            if saved_count == 1:
                self.statusBar().showMessage("Auto-saved 1 file", 2000)
            else:
                self.statusBar().showMessage(f"Auto-saved {saved_count} files", 2000)
            
            
    def format_xml(self):
        """Format the XML content."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        content = editor.get_text().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "No content to format")
            return
        
        try:
            formatted = XMLUtilities.format_xml(content)
            editor.set_text(formatted)
            self.statusBar().showMessage("XML formatted successfully")
            self.refresh_tree_view()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to format XML:\n{str(e)}")
            self.output_panel.setPlainText(f"Format Error:\n{str(e)}")
            self.output_dock.show()
            
    def validate_xml(self):
        """Open validation dialog or show validation panel."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        content = editor.get_text().strip()
        
        # Show validation panel and perform well-formed check
        self.validation_dock.show()
        self.validate_well_formed()
    
    def show_schema_generation_dialog(self):
        """Open schema generation dialog."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        content = editor.get_text().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "No XML content to generate schema from")
            return
        
        dialog = SchemaGenerationDialog(content, self)
        dialog.exec()

    def validate_well_formed(self):
        """Validate XML well-formedness in the validation panel."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        content = editor.get_text().strip()
        if not content:
            self.validation_result.setPlainText("No content to validate")
            return
        
        is_valid, message = XMLUtilities.validate_xml(content)
        
        if is_valid:
            self.validation_result.setStyleSheet("color: green;")
            self.validation_result.setPlainText(f"✓ {message}")
        else:
            self.validation_result.setStyleSheet("color: red;")
            self.validation_result.setPlainText(f"✗ {message}")
    
    def validate_with_xsd(self):
        """Validate XML against XSD schema in the validation panel."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        content = editor.get_text().strip()
        
        if not content:
            self.validation_result.setPlainText("No XML content to validate")
            return
        
        # Get schema content based on active tab
        xsd_content = None
        
        if self.schema_input_tabs.currentIndex() == 0:
            # Text input tab
            xsd_content = self.validation_schema_input.toPlainText().strip()
            if not xsd_content:
                QMessageBox.warning(self, "Warning", "Please provide an XSD schema in the text field")
                return
        else:
            # File path tab - reload from file each time
            if not self.schema_file_path:
                QMessageBox.warning(self, "Warning", "Please select a schema file")
                return
            
            try:
                with open(self.schema_file_path, 'r', encoding='utf-8') as f:
                    xsd_content = f.read()
            except Exception as e:
                self.validation_result.setStyleSheet("color: red;")
                self.validation_result.setPlainText(f"✗ Error loading schema file:\n{str(e)}")
                return
        
        try:
            is_valid, message = XMLUtilities.validate_with_xsd(content, xsd_content)
            
            if is_valid:
                self.validation_result.setStyleSheet("color: green;")
                self.validation_result.setPlainText(f"✓ {message}")
            else:
                self.validation_result.setStyleSheet("color: red;")
                self.validation_result.setPlainText(f"✗ {message}")
        except Exception as e:
            self.validation_result.setStyleSheet("color: red;")
            self.validation_result.setPlainText(f"✗ Error: {str(e)}")
    
    def validate_with_dtd(self):
        """Validate XML against DTD in the validation panel."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        content = editor.get_text().strip()
        
        if not content:
            self.validation_result.setPlainText("No XML content to validate")
            return
        
        # Get DTD content based on active tab
        dtd_content = None
        
        if self.schema_input_tabs.currentIndex() == 0:
            # Text input tab
            dtd_content = self.validation_schema_input.toPlainText().strip()
            if not dtd_content:
                QMessageBox.warning(self, "Warning", "Please provide a DTD in the text field")
                return
        else:
            # File path tab - reload from file each time
            if not self.schema_file_path:
                QMessageBox.warning(self, "Warning", "Please select a DTD file")
                return
            
            try:
                with open(self.schema_file_path, 'r', encoding='utf-8') as f:
                    dtd_content = f.read()
            except Exception as e:
                self.validation_result.setStyleSheet("color: red;")
                self.validation_result.setPlainText(f"✗ Error loading DTD file:\n{str(e)}")
                return
        
        try:
            is_valid, message = XMLUtilities.validate_with_dtd(content, dtd_content)
            
            if is_valid:
                self.validation_result.setStyleSheet("color: green;")
                self.validation_result.setPlainText(f"✓ {message}")
            else:
                self.validation_result.setStyleSheet("color: red;")
                self.validation_result.setPlainText(f"✗ {message}")
        except Exception as e:
            self.validation_result.setStyleSheet("color: red;")
            self.validation_result.setPlainText(f"✗ Error: {str(e)}")
    
    def load_schema_file(self):
        """Load schema or DTD file for validation (text input tab)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Schema/DTD", "", "Schema Files (*.xsd *.dtd);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.validation_schema_input.setPlainText(f.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def select_schema_file(self):
        """Select schema file for validation (file path tab)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Schema/DTD File", "", "Schema Files (*.xsd *.dtd);;All Files (*)"
        )
        
        if file_path:
            self.schema_file_path = file_path
            # Display just the filename with full path as tooltip
            self.schema_file_path_label.setText(os.path.basename(file_path))
            self.schema_file_path_label.setToolTip(file_path)
            self.schema_file_path_label.setStyleSheet("color: black; font-style: normal;")
    
    def clear_schema_file(self):
        """Clear the selected schema file path."""
        self.schema_file_path = None
        self.schema_file_path_label.setText("No file selected")
        self.schema_file_path_label.setToolTip("")
        self.schema_file_path_label.setStyleSheet("color: gray; font-style: italic;")
    
    def load_xslt_text_file(self):
        """Load XSLT file for text input tab."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open XSLT Stylesheet", "", "XSLT Files (*.xsl *.xslt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.xslt_text_input.setPlainText(f.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def select_xslt_file(self):
        """Select XSLT file for file path tab."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select XSLT Stylesheet", "", "XSLT Files (*.xsl *.xslt);;All Files (*)"
        )
        
        if file_path:
            self.xslt_file_path = file_path
            # Display just the filename with full path as tooltip
            self.xslt_file_path_label.setText(os.path.basename(file_path))
            self.xslt_file_path_label.setToolTip(file_path)
            self.xslt_file_path_label.setStyleSheet("color: black; font-style: normal;")
    
    def clear_xslt_file(self):
        """Clear the selected XSLT file path."""
        self.xslt_file_path = None
        self.xslt_file_path_label.setText("No file selected")
        self.xslt_file_path_label.setToolTip("")
        self.xslt_file_path_label.setStyleSheet("color: gray; font-style: italic;")
    
    def apply_xslt_transformation(self):
        """Apply XSLT transformation and display result."""
        editor = self.get_current_editor()
        if not editor:
            QMessageBox.warning(self, "Warning", "No document to transform")
            return
        
        xml_content = editor.get_text().strip()
        if not xml_content:
            QMessageBox.warning(self, "Warning", "No XML content to transform")
            return
        
        # Get XSLT content based on active tab
        xslt_content = None
        if self.xslt_input_tabs.currentIndex() == self.XSLT_TEXT_INPUT_TAB:
            # Text input tab
            xslt_content = self.xslt_text_input.toPlainText().strip()
            if not xslt_content:
                QMessageBox.warning(self, "Warning", "Please provide an XSLT stylesheet")
                return
        else:
            # File path tab
            if not self.xslt_file_path:
                QMessageBox.warning(self, "Warning", "Please select an XSLT file")
                return
            try:
                with open(self.xslt_file_path, 'r', encoding='utf-8') as f:
                    xslt_content = f.read()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load XSLT file:\n{str(e)}")
                return
        
        # Apply transformation
        try:
            result = XMLUtilities.apply_xslt(xml_content, xslt_content)
            # Display result in both tabs
            # Tab 1: XML output with syntax highlighting (default view)
            self.xslt_result_editor.set_text(result)
            # Tab 2: HTML preview
            # Safe: QTextBrowser doesn't support JavaScript, only limited HTML/CSS subset
            # setOpenLinks(False) prevents link activation as additional security measure
            self.xslt_result_browser.setHtml(result)
            # Set default tab to XML output
            self.xslt_result_tabs.setCurrentIndex(self.XSLT_XML_OUTPUT_TAB)
            self.statusBar().showMessage("XSLT transformation completed successfully", 3000)
        except Exception as e:
            error_msg = f"Transformation failed:\n{str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            # Display error in both tabs
            self.xslt_result_editor.set_text(error_msg)
            # Display error in consistent HTML format with proper escaping
            escaped_msg = html.escape(error_msg)
            theme = ThemeManager.get_theme(self.current_theme)
            error_color = theme.get_color('red')
            error_html = f"<div style='color: {error_color}; font-family: monospace; white-space: pre-wrap;'>{escaped_msg}</div>"
            self.xslt_result_browser.setHtml(error_html)
            # Set default tab to XML output
            self.xslt_result_tabs.setCurrentIndex(self.XSLT_XML_OUTPUT_TAB)
        
    def show_xpath_dialog(self):
        """Open XPath query dialog."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        content = editor.get_text().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "No content to query")
            return
        
        # Get the selected node's XPath from the tree view
        context_xpath = self.tree_view.get_selected_xpath()
        
        dialog = XPathDialog(content, context_xpath, self, self.settings)
        dialog.exec()
        
    def show_xslt_dialog(self):
        """Open XSLT transformation dialog."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        content = editor.get_text().strip()
        
        if not content:
            QMessageBox.warning(self, "Warning", "No content to transform")
            return
        
        dialog = XSLTDialog(content, self)
        if dialog.exec():
            transformed = dialog.get_transformed_xml()
            if transformed:
                editor.set_text(transformed)
                self.refresh_tree_view()
                
    def refresh_tree_view(self):
        """Refresh the XML tree view."""
        editor = self.get_current_editor()
        if not editor:
            self.tree_view.clear()
            return
        
        content = editor.get_text().strip()
        
        if content:
            try:
                self.tree_view.load_xml(content, self.show_namespaces)
                self.output_panel.clear()
                self.output_dock.hide()
            except Exception as e:
                self.output_panel.setPlainText(f"Error refreshing tree:\n{str(e)}")
                self.output_dock.show()
        else:
            self.tree_view.clear()
    
    def auto_refresh_tree_view(self):
        """Auto-refresh tree view with error suppression."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        content = editor.get_text().strip()
        
        if content:
            try:
                self.tree_view.load_xml(content, self.show_namespaces)
                # Don't clear/hide output panel during auto-refresh to avoid disruption
            except Exception:
                # Silently fail during auto-refresh (user is still typing)
                pass
            
    def find_text(self):
        """Find text in editor."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        text, ok = QInputDialog.getText(self, "Find", "Find text:")
        if ok and text:
            if not editor.findFirst(text, False, True, False, True):
                QMessageBox.information(self, "Find", f"'{text}' not found")
                
    def replace_text(self):
        """Replace text in editor."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        find_text, ok = QInputDialog.getText(self, "Replace", "Find text:")
        if not ok or not find_text:
            return
        
        replace_text, ok = QInputDialog.getText(self, "Replace", "Replace with:")
        if not ok:
            return
        
        content = editor.get_text()
        new_content = content.replace(find_text, replace_text)
        
        if content != new_content:
            editor.set_text(new_content)
            count = content.count(find_text)
            QMessageBox.information(self, "Replace", f"Replaced {count} occurrence(s)")
        else:
            QMessageBox.information(self, "Replace", f"'{find_text}' not found")
            
    def toggle_comment(self):
        """Toggle XML comment for selected text."""
        editor = self.get_current_editor()
        if not editor:
            return
        
        # Get selected text
        if editor.hasSelectedText():
            start_line, start_pos, end_line, end_pos = editor.getSelection()
            selected_text = editor.selectedText()
            
            # Check if already commented
            if selected_text.strip().startswith('<!--') and selected_text.strip().endswith('-->'):
                # Uncomment
                new_text = selected_text.replace('<!--', '', 1).rsplit('-->', 1)[0]
                editor.replaceSelectedText(new_text)
            else:
                # Comment
                new_text = f"<!-- {selected_text} -->"
                editor.replaceSelectedText(new_text)
        else:
            # Comment current line
            line, pos = editor.getCursorPosition()
            line_text = editor.text(line)
            
            if '<!--' in line_text and '-->' in line_text:
                # Uncomment
                new_text = line_text.replace('<!--', '').replace('-->', '')
            else:
                # Comment
                new_text = f"<!-- {line_text.strip()} -->"
            
            editor.setSelection(line, 0, line, len(line_text))
            editor.replaceSelectedText(new_text)
            
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
    
    def toggle_validation_panel(self):
        """Toggle validation panel visibility."""
        if self.validation_dock.isVisible():
            self.validation_dock.hide()
        else:
            self.validation_dock.show()
    
    def toggle_graph_panel(self):
        """Toggle graph view panel visibility."""
        if self.graph_dock.isVisible():
            self.graph_dock.hide()
        else:
            self.graph_dock.show()
            self.refresh_graph_view()
    
    def toggle_xslt_panel(self):
        """Toggle XSLT panel visibility."""
        if self.xslt_dock.isVisible():
            self.xslt_dock.hide()
        else:
            self.xslt_dock.show()
    
    def toggle_xquery_panel(self):
        """Toggle XQuery panel visibility."""
        if self.xquery_dock.isVisible():
            self.xquery_dock.hide()
        else:
            self.xquery_dock.show()
    
    def toggle_split_view(self, checked):
        """Toggle visibility of the split-view dock."""
        if checked:
            self.split_dock.show()
        else:
            self.split_dock.hide()
    
    def move_tab_to_split_view(self):
        """Move the active tab between the main area and the split-view dock."""
        source_widget = self.get_active_tab_widget()
        index = source_widget.currentIndex()
        if index < 0:
            return
        
        dest_widget = self.split_tab_widget if source_widget is self.tab_widget else self.tab_widget
        data_store_src = self._get_data_store(source_widget)
        tab_data = data_store_src.get(index, {'file_path': None, 'is_modified': False, 'is_pristine': False})
        editor = source_widget.widget(index)
        title = source_widget.tabText(index)
        
        # Remove from source
        source_widget.removeTab(index)
        new_src_data = self._shift_tab_data_after_removal(data_store_src, index)
        if source_widget is self.tab_widget:
            self.tab_data = new_src_data
        else:
            self.split_tab_data = new_src_data
            self._update_split_dock_visibility()
        
        # Show split dock if moving into it
        if dest_widget is self.split_tab_widget:
            self.split_dock.show()
            self.toggle_split_view_action.setChecked(True)
        
        # Add to destination
        new_index = dest_widget.addTab(editor, title)
        dest_widget.setCurrentIndex(new_index)
        dest_store = self._get_data_store(dest_widget)
        dest_store[new_index] = tab_data
        self.editor_tab_map[editor] = dest_widget
        
        self.last_active_editor = editor
        self.update_window_title()
        
    def refresh_graph_view(self):
        """Refresh the XML graph view."""
        editor = self.get_current_editor()
        if not editor:
            self.graph_view.clear()
            return
        
        content = editor.get_text().strip()
        
        if content:
            try:
                self.graph_view.load_xml(content, self.show_namespaces)
            except Exception as e:
                self.statusBar().showMessage(f"Graph view error: {str(e)}", 3000)
        else:
            self.graph_view.clear()
    
    def fit_graph_to_view(self):
        """Fit the graph to the view."""
        self.graph_view.fit_to_view()
            
    def toggle_word_wrap(self, checked):
        """Toggle word wrap in editor."""
        editor = self.get_current_editor()
        if editor:
            if checked:
                editor.setWrapMode(QsciScintilla.WrapMode.WrapWord)
            else:
                editor.setWrapMode(QsciScintilla.WrapMode.WrapNone)
    
    def toggle_show_namespaces(self, checked):
        """Toggle namespace display in tree view."""
        self.show_namespaces = checked
        self.settings.setValue("show_namespaces", checked)
        self.refresh_tree_view()
        status = "shown" if checked else "hidden"
        self.statusBar().showMessage(f"Namespaces {status} in tree view")

    def change_theme(self, theme_type):
        """Change the editor theme."""
        self.current_theme = theme_type
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, XMLEditor):
                editor.apply_theme(theme_type)
        for i in range(self.split_tab_widget.count()):
            editor = self.split_tab_widget.widget(i)
            if isinstance(editor, XMLEditor):
                editor.apply_theme(theme_type)
        
        # Apply theme to XQuery panel
        if hasattr(self, 'xquery_panel'):
            self.xquery_panel.apply_theme(theme_type)
        
        self.settings.setValue("theme", theme_type.value)
        self.statusBar().showMessage(f"Theme changed to {ThemeManager.get_theme_names()[theme_type]}")
            
    def on_text_changed(self):
        """Handle text changed event."""
        tab_widget = self.get_active_tab_widget()
        current_index = tab_widget.currentIndex()
        data_store = self._get_data_store(tab_widget)
        if current_index >= 0:
            tab_data = data_store.get(current_index, {})
            # Only mark as not pristine if this is a user edit (not initial content loading)
            # We detect this by checking if is_modified was already False (initial state)
            if not tab_data.get('is_modified', False):
                # First change - mark as no longer pristine (user has edited)
                tab_data['is_pristine'] = False
            tab_data['is_modified'] = True
            data_store[current_index] = tab_data
            self.update_window_title()
        
        # Restart timer for auto-refreshing tree view (debounce)
        self.tree_refresh_timer.stop()
        self.tree_refresh_timer.start(500)  # Refresh 500ms after user stops typing
        
    def update_window_title(self):
        """Update window title based on current file and modified state."""
        title = "XML Editor"
        
        tab_data = self.get_current_tab_data()
        file_path = tab_data.get('file_path') if tab_data else None
        is_modified = tab_data.get('is_modified', False) if tab_data else False
        
        if file_path:
            title += f" - {os.path.basename(file_path)}"
        else:
            title += " - Untitled"
        
        if is_modified:
            title += " *"
        
        self.setWindowTitle(title)
        view_name = "Split" if self.get_active_tab_widget() is self.split_tab_widget else "Main"
        display_name = os.path.basename(file_path) if file_path else "Untitled"
        self.active_view_label.setText(f"{view_name}: {display_name}")
        
    def check_save_changes(self):
        """Check if there are unsaved changes in any tab and prompt user."""
        for tab_widget, data_store in (
            (self.tab_widget, self.tab_data),
            (self.split_tab_widget, self.split_tab_data)
        ):
            for index in range(tab_widget.count()):
                tab_data = data_store.get(index, {})
                is_modified = tab_data.get('is_modified', False)
                is_pristine = tab_data.get('is_pristine', False)
                
                # Only prompt for save if the tab was actually edited by the user (not pristine)
                if is_modified and not is_pristine:
                    file_path = tab_data.get('file_path')
                    file_name = os.path.basename(file_path) if file_path else 'Untitled'
                    
                    reply = QMessageBox.question(
                        self, "Unsaved Changes",
                        f"Do you want to save changes to {file_name}?",
                        QMessageBox.StandardButton.Save | 
                        QMessageBox.StandardButton.Discard | 
                        QMessageBox.StandardButton.Cancel
                    )
                    
                    if reply == QMessageBox.StandardButton.Save:
                        tab_widget.setCurrentIndex(index)
                        self.last_active_editor = tab_widget.widget(index)
                        self.save_file()
                    elif reply == QMessageBox.StandardButton.Cancel:
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
