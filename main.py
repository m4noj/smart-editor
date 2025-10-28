import sys, os
from PyQt5.QtWidgets import (QApplication, QMainWindow,QTextEdit, QPlainTextEdit, QFileDialog, QAction, QStatusBar, QVBoxLayout,QHBoxLayout, QWidget, QLabel,QMessageBox)
from PyQt5.QtGui import QFont, QPainter, QColor, QTextFormat
from PyQt5.QtCore import QFileInfo
from core.editor import SmartCodeEditor
from highlighter.theme import DEFAULT_DARK, DEFAULT_LIGHT

class SmartEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main Window
        self.setGeometry(100, 100, 1600,800)
        self.setWindowOpacity(0.75)  # 0.0 = transparent, 1.0 = solid
        self.current_file = None
        self.update_title()

        self.editor = SmartCodeEditor()
        self.default_theme()

        self.line_number_widget = LineNumberWidget(self.editor)  
        
        layout = QHBoxLayout()  
        layout.setContentsMargins(0, 0, 0, 0)  # remove spacing
        layout.setSpacing(0)
                
        layout.addWidget(self.line_number_widget)  
        layout.addWidget(self.editor)  # Add the editor

        container = QWidget(self)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.file_stats_label = QLabel()
        self.file_stats_label.setStyleSheet("color: #878585; font-weight:500;margin-right:10px!important;")
        self.editor.textChanged.connect(self.update_stats)
        self.editor.cursorPositionChanged.connect(self.update_stats)
        self.statusBar().addPermanentWidget(self.file_stats_label)
        self.update_stats()

        self.file_type_label = QLabel("Unknown")
        self.file_type_label.setStyleSheet("color: #878585; font-weight:500;margin-right:10px!important;")
        self.statusBar().addPermanentWidget(self.file_type_label)
        self.FILE_TYPES = {'.py':'Python','.txt':'Text','.php':'PHP','.sql': 'SQL','.js': 'JavaScript','.html': 'HTML',''
                           '.css': 'CSS','.md': 'Markdown','.json': 'JSON','.c': 'C','.cpp': 'C++','.java': 'Java','.sh': 'Shell Script' }
        self.update_file_type()   

        self._create_menu()

    def update_title(self):
            if self.current_file:
                name = os.path.basename(self.current_file)
            else:
                name = 'Untitled'

            self.setWindowTitle(f"{name} - Smart Editor")

    def update_file_type(self):
        if self.current_file:
            ext = os.path.splitext(self.current_file)[1].lower()
            lang = self.FILE_TYPES.get(ext,'Unknown')
        else:
            lang = 'Untitled'

        self.file_type_label.setText(f"| {lang}")

    def default_theme(self):
        self.setStyleSheet(""" 
                QMenuBar { background-color: #1e1e1e; color: #ffffff; }
                QMenu::item:hover {background-color: #5c5c5c; color: #ffffff; }
                QStatusBar {background-color: #1e1e1e;color: #ffffff;font-family: Fira Code;font-size: 10pt;}
                QMenu { background-color: #1e1e1e; color: #ffffff;}
                QMenu::item:selected { background-color: #d6dfe7ff; color:#000000; }
                QLabel{color: #ffffff;}
                QMessageBox{background-color:#1e1e1e;}
                """)
        self.editor.set_theme(DEFAULT_DARK)
        self.line_highlight_dark()

    def update_stats(self):
        text = self.editor.toPlainText()
        lines = text.count('\n') + 1
        Words = len(text.split())
        chars = len(text)
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1

        stats_msg = f"Ln: {line} | Col: {col} | Lines: {lines} | words: {Words} | Chars: {chars}"
        self.file_stats_label.setText(stats_msg)
      
    def _create_menu(self):
        menu = self.menuBar()
        menu.setStyleSheet("font-size:14px;")
        
        file_menu = menu.addMenu('File')

        newfile_action = QAction('New',self)
        newfile_action.triggered.connect(self.new_file)
        file_menu.addAction(newfile_action)
        newfile_action.setShortcut("Ctrl+N")

        open_action = QAction('Open',self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        open_action.setShortcut("Ctrl+O")

        save_action = QAction('Save',self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        save_action.setShortcut("Ctrl+S")

        view_menu = menu.addMenu("View")

        terminal_action = QAction('Terminal',self)
        terminal_action.setCheckable(True)
        terminal_action.triggered.connect(self.toggle_terminal)
        view_menu.addAction(terminal_action)
        terminal_action.setShortcut("Alt+C")
        
        theme_action = QAction("Toggle Dark Theme", self)
        theme_action.setCheckable(True)
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        theme_action.setShortcut("Alt+D")
        
        sidebar_action = QAction('Sidebar',self)
        sidebar_action.setCheckable(True)
        sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(sidebar_action)
        sidebar_action.setShortcut("Alt+S")
        
        run_menu = menu.addMenu("Run")

        help_menu = self.menuBar().addMenu("Help")

        features_action = QAction("Features", self)
        features_action.triggered.connect(self.show_features)
        help_menu.addAction(features_action)
        features_action.setShortcut("Ctrl+H")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        about_action.setShortcut("Ctrl+I")

    def new_file(self):
        if self.editor.document().isModified():
            reply = QMessageBox.question(self, "Unsaved Changes", "Do you want to save changes before creating a new file?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                self.save_file()
                if self.editor.document().isModified():
                    return

            elif reply == QMessageBox.Cancel:
                return

        self.editor.clear()
        self.current_file = None
        self.editor.document().setModified(False)
        self.update_title()
        self.update_file_type()
        self.statusBar().showMessage("New file created", 3000)

    def open_file(self):
        if self.editor.document().isModified():
            reply = QMessageBox.question(self, "Unsaved Changes", "Do you want to save changes before opening another file?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                self.save_file()
                if self.editor.document().isModified():
                    return 

            elif reply == QMessageBox.Cancel:
                return

        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*.*)")
        if path:
            with open(path, 'r') as f:
                self.editor.setPlainText(f.read())
            self.statusBar().showMessage(f"Opened: {os.path.basename(path)}", 3000)
            self.current_file = path
            self.editor.document().setModified(False)
            self.update_title()
            self.update_file_type()

    def save_file(self):
        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*.*)")
            if not path:
                return
            self.current_file = path
        else:
            path = self.current_file

        with open(path, 'w') as f:
            f.write(self.editor.toPlainText())
            self.status.showMessage(f"Saved : {QFileInfo(path).fileName()}")
            self.editor.document().setModified(False)

        self.update_title()
        self.update_file_type()

    def show_features(self):        
        QMessageBox.information(self, "SmartEditor - Features", 
        "✔ Save/Open Files\n"
        "✔ Line Numbers\n"
        "✔ Dark & Light Themes\n"
        "✔ Current Line Highlighting\n"
        "✔ Informative Status Bar\n"
        "✔ Basic Shortcuts\n"
        "✔ Syntax Highlighting (Python)\n"
        "✔ Basic File Stats (Line, Cursor)\n\n"
        "✔ Future: Autocomplete, Code Hints & other updates."
    )

    def show_about(self):
        QMessageBox.information(self, "About SmartEditor",
        "SmartEditor v1.0\n"
        "A clean, Lightweight and Intelligent code editor.\n"
        "Built from scratch in Python with PyQt5\n\n\n"
        "Crafted by : Manoj Borkar\n"
        "© 2025 Manoj. All rights reserved.")
    
    def toggle_sidebar(self):
        pass
   
    def toggle_terminal(self):
        pass

    # function for activating Highlight Current Line : LIGHT MODE
    def line_highlight_light(self):
        self.editor.cursorPositionChanged.connect(self.highlight_current_line_Light)
        self.highlight_current_line_Light()

    # function for activating Highlight Current Line : DARK MODE
    def line_highlight_dark(self):
        self.editor.cursorPositionChanged.connect(self.highlight_current_line_Dark)
        self.highlight_current_line_Dark()

    def toggle_theme(self,enabled):
        if enabled:
            # Light Theme
            self.setStyleSheet("""
                QMenuBar { background-color: #d6dfe7ff; color: #000000; }
                QMenu::item:hover { background-color: #3c3c3c; color:#ffffff; }
                QStatusBar {background-color: #d6dfe7ff;color: #000000;font-family: Fira Code;font-size: 10pt;}
                QMenu { background-color: #d6dfe7ff; color: #000000; }
                QMenuBar::item:selected { background-color: #3c3c3c; color:#ffffff; }
                QLabel{color: #000000;}
                QMessageBox{background-color:#d6dfe7ff;}
            """)
            self.editor.set_theme(DEFAULT_LIGHT)
            self.line_highlight_light()
        else: 
            # Dark Theme
            self.setStyleSheet(""" 
                QMenuBar { background-color: #1e1e1e; color: #ffffff; }
                QMenu::item:hover {background-color: #5c5c5c; color: #ffffff; }
                QStatusBar {background-color: #1e1e1e;color: #ffffff;font-family: Fira Code;font-size: 10pt;}
                QMenu { background-color: #1e1e1e; color: #ffffff;}
                QMenu::item:selected { background-color: #d6dfe7ff; color:#000000; }
                QLabel{color: #ffffff;}
                QMessageBox{background-color:#1e1e1e;}
            """)
            self.editor.set_theme(DEFAULT_DARK)
            self.line_highlight_dark()

    # Function for Highlight Current Line : LIGHT
    def highlight_current_line_Light(self):
        selection = QTextEdit.ExtraSelection()
        line_color = QColor(self.editor.highlight_color)  # Light highlight for the current line
        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.editor.textCursor()
        selection.cursor.clearSelection()
        self.editor.setExtraSelections([selection])


    # Function for Highlight Current Line : DARK
    def highlight_current_line_Dark(self):
        selection = QTextEdit.ExtraSelection()
        line_color = QColor(self.editor.highlight_color)  # Dark highlight for the current line
        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.editor.textCursor()
        selection.cursor.clearSelection()
        self.editor.setExtraSelections([selection])

    def closeEvent(self, event):
        if self.editor.document().isModified():
            reply = QMessageBox.question(self,"Unsaved Changes", "Do you want to save changes before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                self.save_file()
                if self.editor.document().isModified():
                    event.ignore()
                    return

            elif reply == QMessageBox.Cancel:
                event.ignore()
                return

        event.accept()  # Close the app

class LineNumberWidget(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor  # Reference to the code editor (QPlainTextEdit)

        self.editor.blockCountChanged.connect(self.update)        
        self.editor.updateRequest.connect(self.update_area)       
        self.editor.textChanged.connect(self.update)              

        self.editor.blockCountChanged.connect(self.update_width)
        self.update_width()

        self.setMinimumWidth(40)

    def update_width(self):
        digits = len(str(self.editor.blockCount()))
        space = 25 + self.fontMetrics().horizontalAdvance('10') * digits
        self.setFixedWidth(space)

    def update_area(self, rect, dy):
        if dy:
            self.scroll(0, dy)  
        else:
            self.update(0, rect.y(), self.width(), rect.height())

        if rect.contains(self.editor.viewport().rect()):
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)  
        painter.fillRect(event.rect(),QColor(self.editor.current_theme['background']))

        painter.setPen(QColor(125,122,122))
        painter.setFont(QFont("monospace", 14))

        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()  

        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).y()
        bottom = top + self.editor.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)  

                painter.drawText(5, int(top + 15), number)

            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1

    def sizeHint(self):
        return self.editor.viewport().size()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = SmartEditor()
    editor.show()
    sys.exit(app.exec_())
