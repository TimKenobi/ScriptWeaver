# app/gui/in_app_editor_dialog.py

import logging
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox, QMessageBox
from PyQt6.QtGui import QFontDatabase

class InAppEditorDialog(QDialog):
    """
    A simple dialog window for editing the content of a script file.
    """
    def __init__(self, script_path: Path, parent=None):
        super().__init__(parent)
        self.script_path = script_path
        self.setWindowTitle(f"Editing: {self.script_path.name}")
        self.setMinimumSize(800, 600)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Main text editor widget
        self.editor = QTextEdit()
        # Use a monospaced font for better code readability
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self.editor.setFont(font)
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # Common for code editors
        layout.addWidget(self.editor)

        # Standard Save/Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.load_script_content()

    def load_script_content(self):
        """Reads the content from the script file and populates the editor."""
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
        except Exception as e:
            logging.error(f"Failed to load script content from {self.script_path}: {e}")
            self.editor.setPlainText(f"# ERROR: Could not load file.\n# {e}")
            QMessageBox.critical(self, "Error", f"Failed to load script file: {e}")

    def save_and_accept(self):
        """Saves the editor content back to the script file."""
        try:
            with open(self.script_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            logging.info(f"Saved changes to script file: {self.script_path}")
            self.accept()
        except Exception as e:
            logging.error(f"Failed to save script content to {self.script_path}: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save script file: {e}")

