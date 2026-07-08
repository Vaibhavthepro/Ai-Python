from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor, QColor
from history import HistoryManager

class TerminalSession(QPlainTextEdit):
    command_entered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                border: none;
                padding: 5px;
            }
        """)
        self.setUndoRedoEnabled(False)
        self.prompt_position = 0
        self.history = HistoryManager()

    def write_output(self, text, color="#D4D4D4"):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        
        fmt = cursor.charFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        
        cursor.insertText(text)
        self.prompt_position = cursor.position()
        self.ensureCursorVisible()

    def _replace_current_command(self, new_cmd):
        cursor = self.textCursor()
        cursor.setPosition(self.prompt_position)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(new_cmd)
        self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        
        if event.key() == Qt.Key_Up:
            self._replace_current_command(self.history.get_previous())
            return
        elif event.key() == Qt.Key_Down:
            self._replace_current_command(self.history.get_next())
            return

        # Prevent moving cursor or editing before the current prompt
        if event.key() in (Qt.Key_Backspace, Qt.Key_Left):
            if cursor.position() <= self.prompt_position:
                return

        if event.key() == Qt.Key_Home:
            cursor.setPosition(self.prompt_position)
            self.setTextCursor(cursor)
            return

        # If they type while somewhere else, move to end
        if cursor.position() < self.prompt_position and event.text():
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)

        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)
            
            command = self.toPlainText()[self.prompt_position:].strip()
            self.history.add_command(command)
            
            self.command_entered.emit(command)
            
            # Insert newline in the UI
            cursor.insertText("\n")
            self.prompt_position = cursor.position()
            return

        super().keyPressEvent(event)
