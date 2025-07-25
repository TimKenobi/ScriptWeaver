# app/gui/script_output_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QProgressBar, QPushButton,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QTextCursor # <-- Import QTextCursor

class ScriptOutputDialog(QDialog):
    """
    A dialog to show real-time output and progress of a running script.
    """
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self.output_text.setFont(font)
        self.output_text.setStyleSheet("background-color: #2E2E2E; color: #EAEAEA;")
        layout.addWidget(self.output_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        layout.addWidget(self.progress_bar)

        self.button_box = QDialogButtonBox()
        self.close_button = self.button_box.addButton("Close", QDialogButtonBox.ButtonRole.AcceptRole)
        self.close_button.setEnabled(False)
        self.button_box.accepted.connect(self.accept)
        layout.addWidget(self.button_box)

    def append_output(self, text):
        """Appends text to the output window and scrolls to the bottom."""
        # This is the corrected method to avoid the AttributeError
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)
        self.output_text.insertPlainText(text)
        self.output_text.ensureCursorVisible()

    def mark_as_finished(self, success):
        """Called when the script process is finished."""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        if success:
            self.setWindowTitle(f"[SUCCESS] {self.windowTitle()}")
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        else:
            self.setWindowTitle(f"[FAILED] {self.windowTitle()}")
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")

        self.close_button.setEnabled(True)
        self.close_button.setFocus()

    def mark_as_failed(self):
        """Convenience method to explicitly fail the dialog."""
        self.mark_as_finished(success=False)
