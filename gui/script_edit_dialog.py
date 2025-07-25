# app/gui/script_edit_dialog.py

import logging
import shutil
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QCheckBox, QDialogButtonBox, QWidget, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox
)

class ScriptEditDialog(QDialog):
    """
    A dialog for adding a new script or editing an existing one.
    Includes functionality to upload a script file.
    """
    def __init__(self, script_dir: Path, script_data=None, existing_ids=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Script Details" if script_data else "Add New Script")
        self.setMinimumWidth(500)

        self.script_dir = script_dir
        self.is_edit_mode = script_data is not None
        self.script_data = script_data or {}
        self.existing_ids = existing_ids or []
        
        # --- UI Setup ---
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.id_input = QLineEdit(self.script_data.get("id", ""))
        self.id_input.setToolTip("A unique, lowercase identifier used internally (e.g., 'install_office').\nCannot be changed after creation.")
        self.id_input.setPlaceholderText("unique_script_id")
        if self.is_edit_mode:
            self.id_input.setReadOnly(True)
            
        self.name_input = QLineEdit(self.script_data.get("name", ""))
        self.name_input.setToolTip("The user-friendly name displayed on buttons in the UI.")
        self.name_input.setPlaceholderText("Install Microsoft Office")
        
        # --- Path input with Browse button ---
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)
        path_layout.setContentsMargins(0,0,0,0)
        self.path_input = QLineEdit(self.script_data.get("path", ""))
        self.path_input.setToolTip("The exact filename of the script that exists in the 'scripts' folder.")
        self.path_input.setPlaceholderText("install_office.sh")
        browse_button = QPushButton("Browse...")
        browse_button.setToolTip("Browse for a script file. This will copy it to the scripts folder and fill out the fields.")
        browse_button.clicked.connect(self.browse_for_script)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)
        
        self.desc_input = QTextEdit(self.script_data.get("description", ""))
        self.desc_input.setToolTip("A short description of what the script does. This appears in tooltips and confirmation dialogs.")
        self.desc_input.setFixedHeight(80)
        
        self.category_input = QComboBox()
        self.category_input.setToolTip("The tab where this script will appear in the 'Advanced Features' section.")
        categories = sorted(["Tools", "Software", "Configuration", "Uninstall"])
        if (cat := self.script_data.get("category")) and cat not in categories:
            categories.append(cat)
        self.category_input.addItems(categories)
        self.category_input.setEditable(True)
        self.category_input.setCurrentText(self.script_data.get("category", "Tools"))

        self.needs_sudo_checkbox = QCheckBox()
        self.needs_sudo_checkbox.setToolTip("Check this if the script needs to be run with 'sudo' (administrator privileges).")
        self.needs_sudo_checkbox.setChecked(self.script_data.get("needs_sudo", False))

        self.uninstall_id_input = QLineEdit(self.script_data.get("uninstall_id", ""))
        self.uninstall_id_input.setToolTip("Optional: If this is an installer, enter the ID of the corresponding uninstall script here.")
        self.uninstall_id_input.setPlaceholderText("e.g., uninstall_office")

        form_layout.addRow("ID:", self.id_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Script Filename:", path_widget)
        form_layout.addRow("Description:", self.desc_input)
        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("Needs Sudo:", self.needs_sudo_checkbox)
        form_layout.addRow("Uninstall Script ID:", self.uninstall_id_input)
        
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def browse_for_script(self):
        """Opens a file dialog to select and copy a script file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Script File", "", "Shell Scripts (*.sh);;All Files (*)")
        
        if not file_path:
            return

        source_path = Path(file_path)
        dest_path = self.script_dir / source_path.name

        if dest_path.exists() and source_path.resolve() != dest_path.resolve():
            reply = QMessageBox.question(self, "File Exists", 
                f"The file '{dest_path.name}' already exists in the scripts directory. Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return

        try:
            shutil.copy(source_path, dest_path)
            logging.info(f"Copied script from {source_path} to {dest_path}")
            
            self.path_input.setText(dest_path.name)
            if not self.id_input.text():
                suggested_id = dest_path.stem.replace("-", "_").lower()
                self.id_input.setText(suggested_id)
            if not self.name_input.text():
                suggested_name = dest_path.stem.replace("-", " ").replace("_", " ").title()
                self.name_input.setText(suggested_name)

        except Exception as e:
            logging.error(f"Failed to copy script file: {e}")
            QMessageBox.critical(self, "Error", f"Could not copy file: {e}")

    def validate_and_accept(self):
        new_id = self.id_input.text().strip()
        
        if not new_id or not self.name_input.text().strip() or not self.path_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "ID, Name, and Script Filename are required fields.")
            return

        if not self.is_edit_mode and new_id in self.existing_ids:
            QMessageBox.warning(self, "Validation Error", f"The script ID '{new_id}' already exists. Please choose a unique ID.")
            return
            
        self.accept()

    def get_data(self):
        data = {
            "id": self.id_input.text().strip(),
            "name": self.name_input.text().strip(),
            "path": self.path_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "category": self.category_input.currentText().strip(),
            "needs_sudo": self.needs_sudo_checkbox.isChecked(),
        }
        uninstall_id = self.uninstall_id_input.text().strip()
        if uninstall_id:
            data["uninstall_id"] = uninstall_id
        return data
