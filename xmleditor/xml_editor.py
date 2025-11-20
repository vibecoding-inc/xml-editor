"""
XML Editor widget with syntax highlighting using QScintilla.
"""

from PyQt6.Qsci import QsciScintilla, QsciLexerXML
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt


class XMLEditor(QsciScintilla):
    """XML editor with syntax highlighting and advanced features."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up the font
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setMarginsFont(font)
        
        # Set up line numbers
        fontmetrics = self.fontMetrics()
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.horizontalAdvance("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#f0f0f0"))
        self.setMarginsForegroundColor(QColor("#333333"))
        
        # Set up the XML lexer for syntax highlighting
        lexer = QsciLexerXML(self)
        lexer.setFont(font)
        self.setLexer(lexer)
        
        # Set indentation
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setAutoIndent(True)
        
        # Set folding
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setFoldMarginColors(QColor("#f0f0f0"), QColor("#f0f0f0"))
        
        # Set caret
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))
        self.setCaretWidth(2)
        
        # Set edge mode
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(80)
        self.setEdgeColor(QColor("#e0e0e0"))
        
        # Enable brace matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setMatchedBraceBackgroundColor(QColor("#b4eeb4"))
        self.setUnmatchedBraceForegroundColor(QColor("#ff0000"))
        
        # Set selection colors
        self.setSelectionBackgroundColor(QColor("#b3d4fc"))
        
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
        
    def get_text(self):
        """Get the text content of the editor."""
        return self.text()
    
    def set_text(self, text):
        """Set the text content of the editor."""
        self.setText(text)
        
    def clear_content(self):
        """Clear the editor content."""
        self.clear()
