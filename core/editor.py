from os import name
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from PyQt5.QtCore import Qt
from highlighter import theme
import highlighter
from highlighter.lexer import lex_line
from highlighter.theme import DEFAULT_DARK,DEFAULT_LIGHT

class SmartCodeEditor(QPlainTextEdit):
    def __init__(self, theme=DEFAULT_DARK, parent=None):
        super().__init__(parent)
        self.current_theme = theme
        self.highlight_color = self.current_theme['highlight']
        self.setFont(QFont("monospace", 14))
        self.textChanged.connect(self.highlight_all)
        self.setPlainText("def hello_world():\n    print('Hello, World!')\n")

    # new theme fn
    def set_theme(self, theme: dict):
        self.current_theme = theme
        self.highlight_color = self.current_theme['highlight']
        self.setStyleSheet(f"background-color: {self.current_theme['background']}; color: {self.current_theme['foreground']};")
        self.highlight_all()

    def highlight_all(self):
        self.blockSignals(True)
        cursor = QTextCursor(self.document())

        block = self.document().firstBlock()
        while block.isValid():
            text = block.text()
            block_position = block.position()
            tokens = lex_line(text)

            for token_type, start, end in tokens:
                fmt = QTextCharFormat()
                fmt.setForeground(QColor(self.current_theme.get(token_type, "#ffffff")))
                if (token_type == "keywords" or token_type == "keywords2" or token_type == "keywords3" 
                    or token_type == "keywords4" or token_type == "bool" or token_type == "operator" 
                    or token_type == "builtin" or token_type == "type"):
                    fmt.setFontWeight(QFont.Bold)
                cursor.setPosition(block_position + start)
                cursor.setPosition(block_position + end, QTextCursor.KeepAnchor)
                cursor.setCharFormat(fmt)

            block = block.next()

        self.blockSignals(False)
