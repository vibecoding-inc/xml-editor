"""
XML Editor widget with syntax highlighting using QScintilla.
"""

from PyQt6.Qsci import QsciScintilla, QsciLexerXML
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from xmleditor.theme_manager import ThemeManager, ThemeType


class XMLEditor(QsciScintilla):
    """XML editor with syntax highlighting and advanced features."""
    
    def __init__(self, parent=None, theme_type=ThemeType.SYSTEM):
        super().__init__(parent)
        
        # Set up the font
        self.font = QFont("Courier New", 10)
        self.font.setFixedPitch(True)
        self.setFont(self.font)
        self.setMarginsFont(self.font)
        
        # Store theme type
        self.theme_type = theme_type
        
        # Set up line numbers
        fontmetrics = self.fontMetrics()
        self.setMarginsFont(self.font)
        self.setMarginWidth(0, fontmetrics.horizontalAdvance("00000") + 6)
        self.setMarginLineNumbers(0, True)
        
        # Set up the XML lexer for syntax highlighting
        self.lexer = QsciLexerXML(self)
        self.lexer.setFont(self.font)
        self.setLexer(self.lexer)
        
        # Set indentation
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setAutoIndent(True)
        
        # Set folding
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        
        # Set caret
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        
        # Set edge mode
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(80)
        
        # Enable brace matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        
        # Enable auto-completion
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(True)
        
        # Enable UTF-8
        self.setUtf8(True)
        
        # Set EOL mode to Unix
        self.setEolMode(QsciScintilla.EolMode.EolUnix)
        self.setEolVisibility(False)
        
        # Enable word wrap
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)
        
        # Enable whitespace visibility (optional)
        self.setWhitespaceVisibility(QsciScintilla.WhitespaceVisibility.WsInvisible)
        
        # Apply initial theme
        self.apply_theme(theme_type)
    
    def apply_theme(self, theme_type):
        """Apply a theme to the editor."""
        self.theme_type = theme_type
        theme = ThemeManager.get_theme(theme_type)
        
        # Apply background and text colors
        self.setPaper(QColor(theme.get_color("base")))
        self.setColor(QColor(theme.get_color("text")))
        
        # Apply margin colors (line numbers)
        self.setMarginsBackgroundColor(QColor(theme.get_color("surface0")))
        self.setMarginsForegroundColor(QColor(theme.get_color("subtext1")))
        
        # Apply fold margin colors
        fold_bg = QColor(theme.get_color("surface0"))
        self.setFoldMarginColors(fold_bg, fold_bg)
        
        # Apply caret line color
        self.setCaretLineBackgroundColor(QColor(theme.get_color("caret_line")))
        self.setCaretForegroundColor(QColor(theme.get_color("text")))
        
        # Apply edge color
        self.setEdgeColor(QColor(theme.get_color("edge_color")))
        
        # Apply brace matching colors
        self.setMatchedBraceBackgroundColor(QColor(theme.get_color("matched_brace")))
        self.setUnmatchedBraceForegroundColor(QColor(theme.get_color("red")))
        
        # Apply selection colors
        self.setSelectionBackgroundColor(QColor(theme.get_color("selection")))
        self.setSelectionForegroundColor(QColor(theme.get_color("text")))
        
        # Apply lexer colors for syntax highlighting
        self._apply_lexer_theme(theme)
        
        # Refresh the display
        self.update()
    
    def _apply_lexer_theme(self, theme):
        """Apply theme colors to the XML lexer."""
        if not self.lexer:
            return
        
        # Set default colors
        self.lexer.setDefaultPaper(QColor(theme.get_color("base")))
        self.lexer.setDefaultColor(QColor(theme.get_color("text")))
        
        # QsciLexerXML style definitions:
        # 0: Default
        # 1: Tag
        # 2: Unknown tag
        # 3: Attribute
        # 4: Unknown attribute
        # 5: Number
        # 6: Double quoted string
        # 7: Single quoted string
        # 8: Other inside tag
        # 9: Comment
        # 10: Entity
        # 11: End of a tag
        # 12: Start of an XML fragment
        # 13: End of an XML fragment
        # 14: Script tag
        # 15: Start of an ASP fragment with @
        # 16: Start of an ASP fragment
        # 17: CDATA
        # 18: PHP script tag
        
        # Apply colors for each style
        styles = {
            0: ("text", None),                      # Default
            1: ("mauve", None),                     # Tag (e.g., <tag>)
            2: ("red", None),                       # Unknown tag
            3: ("green", None),                     # Attribute name
            4: ("red", None),                       # Unknown attribute
            5: ("peach", None),                     # Number
            6: ("yellow", None),                    # Double quoted string
            7: ("yellow", None),                    # Single quoted string
            8: ("text", None),                      # Other inside tag
            9: ("subtext0", None),                  # Comment
            10: ("teal", None),                     # Entity (e.g., &amp;)
            11: ("mauve", None),                    # End tag
            12: ("mauve", None),                    # Start of XML fragment
            13: ("mauve", None),                    # End of XML fragment
            14: ("mauve", None),                    # Script tag
            15: ("blue", None),                     # ASP with @
            16: ("blue", None),                     # ASP
            17: ("pink", None),                     # CDATA
            18: ("blue", None),                     # PHP
        }
        
        for style_num, (fg_key, bg_key) in styles.items():
            fg_color = QColor(theme.get_color(fg_key))
            self.lexer.setColor(fg_color, style_num)
            
            if bg_key:
                bg_color = QColor(theme.get_color(bg_key))
                self.lexer.setPaper(bg_color, style_num)
            else:
                self.lexer.setPaper(QColor(theme.get_color("base")), style_num)
            
            # Keep the font for all styles
            self.lexer.setFont(self.font, style_num)
        
    def get_text(self):
        """Get the text content of the editor."""
        return self.text()
    
    def set_text(self, text):
        """Set the text content of the editor."""
        self.setText(text)
        
    def clear_content(self):
        """Clear the editor content."""
        self.clear()
