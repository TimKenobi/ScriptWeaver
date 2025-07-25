# app/gui/settings_window.py

import logging
import json
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QPushButton, QMessageBox, QSplitter,
    QLabel, QInputDialog, QLineEdit, QFormLayout, QSpinBox,
    QFileDialog, QGroupBox, QTextEdit
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from app.utils.config_manager import load_config, save_config, reset_to_defaults
from app.gui.script_edit_dialog import ScriptEditDialog
from app.gui.in_app_editor_dialog import InAppEditorDialog
from app.config import settings as app_settings

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings and Configuration")
        self.setMinimumSize(900, 700)
        self.setModal(True)

        self.general_config, self.scripts_config, self.workflows_config = load_config()

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.create_general_tab()
        self.create_scripts_tab()
        self.create_workflows_tab()
        
        button_layout = QHBoxLayout()
        self.save_button = QPushButton(QIcon.fromTheme("document-save"), "Save and Close")
        self.save_button.setObjectName("SaveButton")
        self.save_button.clicked.connect(self.save_and_close)
        
        self.cancel_button = QPushButton(QIcon.fromTheme("window-close"), "Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def create_general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        form_group = QGroupBox("Application Settings")
        form_layout = QFormLayout(form_group)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.app_name_input = QLineEdit(self.general_config.get("APP_NAME", ""))
        self.company_name_input = QLineEdit(self.general_config.get("COMPANY_NAME", ""))
        self.max_attempts_input = QSpinBox()
        self.max_attempts_input.setRange(1, 10)
        self.max_attempts_input.setValue(self.general_config.get("MAX_LOGIN_ATTEMPTS", 3))
        logo_path_widget = QHBoxLayout()
        self.logo_path_input = QLineEdit(self.general_config.get("LOGO_PATH", ""))
        self.logo_path_input.setPlaceholderText("e.g., assets/logo.png")
        browse_logo_button = QPushButton("Browse...")
        browse_logo_button.clicked.connect(self.browse_for_logo)
        logo_path_widget.addWidget(self.logo_path_input)
        logo_path_widget.addWidget(browse_logo_button)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Leave blank to keep current password")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Application Name:", self.app_name_input)
        form_layout.addRow("Company Name:", self.company_name_input)
        form_layout.addRow("Logo Path:", logo_path_widget)
        form_layout.addRow("Max Login Attempts:", self.max_attempts_input)
        form_layout.addRow("New Application Password:", self.new_password_input)
        form_layout.addRow("Confirm New Password:", self.confirm_password_input)
        layout.addWidget(form_group)
        
        layout.addStretch()

        bottom_layout = QHBoxLayout()
        reset_button = QPushButton(QIcon.fromTheme("edit-undo"), "Reset Application to Defaults...")
        reset_button.setStyleSheet("background-color: #c0392b;")
        reset_button.clicked.connect(self.reset_application)
        bottom_layout.addWidget(reset_button)
        bottom_layout.addStretch()
        export_button = QPushButton(QIcon.fromTheme("document-export"), "Export Settings...")
        export_button.clicked.connect(self.export_settings)
        import_button = QPushButton(QIcon.fromTheme("document-import"), "Import Settings...")
        import_button.clicked.connect(self.import_settings)
        bottom_layout.addWidget(export_button)
        bottom_layout.addWidget(import_button)
        layout.addLayout(bottom_layout)

        self.tabs.addTab(tab, "General")

    def reset_application(self):
        reply = QMessageBox.critical(self, "Confirm Reset",
            "<b>This will reset all application settings, including scripts, workflows, and the admin password.</b><br><br>"
            "The application will close, and you will be prompted to run the first-time setup on next launch. "
            "This action cannot be undone.<br><br>Are you sure you want to proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if reset_to_defaults():
                QMessageBox.information(self, "Reset Complete", "Application has been reset to defaults. Please restart the application.")
                self.parent().close()
            else:
                QMessageBox.critical(self, "Error", "Failed to reset application. Check logs for details.")
        
    def browse_for_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Logo File", "", "Images (*.png *.jpg *.jpeg *.svg)")
        if not file_path:
            return
        source_path = Path(file_path)
        assets_dir = app_settings.ASSETS_DIR
        assets_dir.mkdir(exist_ok=True)
        dest_filename = "logo" + source_path.suffix
        dest_path = assets_dir / dest_filename
        try:
            shutil.copy(source_path, dest_path)
            relative_path = dest_path.relative_to(app_settings.APP_DIR)
            self.logo_path_input.setText(str(relative_path))
            logging.info(f"Copied new logo to {dest_path}")
        except Exception as e:
            logging.error(f"Failed to copy logo file: {e}")
            QMessageBox.critical(self, "Error", f"Could not copy logo file: {e}")

    def create_scripts_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        self.script_list_widget = QListWidget()
        self.populate_script_list()
        self.script_list_widget.itemSelectionChanged.connect(self.update_script_button_states)
        layout.addWidget(self.script_list_widget)
        
        button_vbox = QVBoxLayout()
        add_button = QPushButton(QIcon.fromTheme("list-add"), "Add New Script...")
        self.edit_button = QPushButton(QIcon.fromTheme("document-edit"), "Edit Details...")
        self.remove_button = QPushButton(QIcon.fromTheme("list-remove"), "Remove Selected")
        
        button_vbox.addSpacing(20)
        self.edit_file_button = QPushButton(QIcon.fromTheme("accessories-text-editor"), "Edit Script File...")
        self.edit_file_button.clicked.connect(self.edit_script_file)

        add_button.clicked.connect(self.add_script)
        self.edit_button.clicked.connect(self.edit_script)
        self.remove_button.clicked.connect(self.remove_script)
        
        button_vbox.addWidget(add_button)
        button_vbox.addWidget(self.edit_button)
        button_vbox.addWidget(self.remove_button)
        button_vbox.addSpacing(20)
        button_vbox.addWidget(self.edit_file_button)
        button_vbox.addStretch()
        
        layout.addLayout(button_vbox)
        self.tabs.addTab(tab, "Manage Scripts")
        self.update_script_button_states()

    def create_workflows_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Workflows"))
        self.workflow_list_widget = QListWidget()
        self.workflow_list_widget.itemSelectionChanged.connect(self.workflow_selection_changed)
        left_layout.addWidget(self.workflow_list_widget)

        wf_button_layout = QHBoxLayout()
        add_wf_button = QPushButton("Add...")
        add_wf_button.clicked.connect(self.add_workflow)
        self.remove_wf_button = QPushButton("Remove")
        self.remove_wf_button.clicked.connect(self.remove_workflow)
        wf_button_layout.addWidget(add_wf_button)
        wf_button_layout.addWidget(self.remove_wf_button)
        left_layout.addLayout(wf_button_layout)
        
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)

        details_group = QGroupBox("Workflow Details")
        details_layout = QFormLayout()
        self.workflow_name_input = QLineEdit()
        self.workflow_desc_input = QTextEdit()
        self.workflow_desc_input.setFixedHeight(60)
        details_layout.addRow("Name:", self.workflow_name_input)
        details_layout.addRow("Description:", self.workflow_desc_input)
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)

        self.workflow_name_input.textChanged.connect(self.update_workflow_details)
        self.workflow_desc_input.textChanged.connect(self.update_workflow_details)

        script_editor_widget = QWidget()
        script_editor_layout = QHBoxLayout(script_editor_widget)
        
        included_layout = QVBoxLayout()
        included_layout.addWidget(QLabel("Included Scripts (In Order)"))
        self.included_scripts_widget = QListWidget()
        self.included_scripts_widget.itemSelectionChanged.connect(self.update_workflow_button_states)
        included_layout.addWidget(self.included_scripts_widget)

        move_btn_layout = QHBoxLayout()
        self.move_up_button = QPushButton(QIcon.fromTheme("go-up"), "Move Up")
        self.move_up_button.clicked.connect(lambda: self.move_script_in_workflow(-1))
        self.move_down_button = QPushButton(QIcon.fromTheme("go-down"), "Move Down")
        self.move_down_button.clicked.connect(lambda: self.move_script_in_workflow(1))
        move_btn_layout.addWidget(self.move_up_button)
        move_btn_layout.addWidget(self.move_down_button)
        included_layout.addLayout(move_btn_layout)

        add_remove_layout = QVBoxLayout()
        add_remove_layout.addStretch()
        self.add_script_to_wf_button = QPushButton(QIcon.fromTheme("go-previous"), "  <-- Add  ")
        self.add_script_to_wf_button.clicked.connect(self.add_script_to_workflow)
        self.remove_script_from_wf_button = QPushButton(QIcon.fromTheme("go-next"), "  Remove -->  ")
        self.remove_script_from_wf_button.clicked.connect(self.remove_script_from_workflow)
        add_remove_layout.addWidget(self.add_script_to_wf_button)
        add_remove_layout.addWidget(self.remove_script_from_wf_button)
        add_remove_layout.addStretch()

        available_layout = QVBoxLayout()
        available_layout.addWidget(QLabel("Available Scripts"))
        self.available_scripts_widget = QListWidget()
        self.available_scripts_widget.itemSelectionChanged.connect(self.update_workflow_button_states)
        available_layout.addWidget(self.available_scripts_widget)

        script_editor_layout.addLayout(included_layout)
        script_editor_layout.addLayout(add_remove_layout)
        script_editor_layout.addLayout(available_layout)
        right_layout.addWidget(script_editor_widget)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_pane)
        splitter.setSizes([250, 650])
        layout.addWidget(splitter)
        
        self.tabs.addTab(tab, "Manage Workflows")
        self.populate_workflow_list()
        self.update_workflow_button_states()

    def export_settings(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Settings", "script_manager_backup.json", "JSON Files (*.json)")
        if not file_path:
            return
        self.gather_ui_data()
        full_config = {
            "general": self.general_config,
            "scripts": self.scripts_config,
            "workflows": self.workflows_config
        }
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=4)
            QMessageBox.information(self, "Success", f"Settings successfully exported to {file_path}")
        except Exception as e:
            logging.error(f"Failed to export settings: {e}")
            QMessageBox.critical(self, "Error", f"Could not export settings: {e}")

    def import_settings(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Settings", "", "JSON Files (*.json)")
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            if not all(k in imported_config for k in ["general", "scripts", "workflows"]):
                raise ValueError("Invalid configuration file. Missing required keys.")
            self.general_config = imported_config["general"]
            self.scripts_config = imported_config["scripts"]
            self.workflows_config = imported_config["workflows"]
            self.repopulate_all_tabs()
            QMessageBox.information(self, "Success", "Settings imported. Review the changes and click 'Save and Close' to apply them.")
        except Exception as e:
            logging.error(f"Failed to import settings: {e}")
            QMessageBox.critical(self, "Error", f"Could not import settings: {e}")

    def repopulate_all_tabs(self):
        self.app_name_input.setText(self.general_config.get("APP_NAME", ""))
        self.company_name_input.setText(self.general_config.get("COMPANY_NAME", ""))
        self.logo_path_input.setText(self.general_config.get("LOGO_PATH", ""))
        self.max_attempts_input.setValue(self.general_config.get("MAX_LOGIN_ATTEMPTS", 3))
        self.new_password_input.clear()
        self.confirm_password_input.clear()
        self.populate_script_list()
        self.populate_workflow_list()
        self.workflow_selection_changed()

    def gather_ui_data(self):
        self.general_config['APP_NAME'] = self.app_name_input.text()
        self.general_config['COMPANY_NAME'] = self.company_name_input.text()
        self.general_config['LOGO_PATH'] = self.logo_path_input.text()
        self.general_config['MAX_LOGIN_ATTEMPTS'] = self.max_attempts_input.value()
        new_password = self.new_password_input.text()
        if new_password:
            self.general_config['new_password'] = new_password

    def populate_script_list(self):
        self.script_list_widget.clear()
        sorted_scripts = sorted(self.scripts_config, key=lambda s: s['name'].lower())
        for script in sorted_scripts:
            item = QListWidgetItem(f"{script['name']} ({script['id']})")
            item.setData(Qt.ItemDataRole.UserRole, script['id'])
            self.script_list_widget.addItem(item)

    def update_script_button_states(self):
        has_selection = len(self.script_list_widget.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)
        self.edit_file_button.setEnabled(has_selection)

    def add_script(self):
        existing_ids = [s['id'] for s in self.scripts_config]
        dialog = ScriptEditDialog(script_dir=app_settings.SCRIPT_DIR, existing_ids=existing_ids, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            self.scripts_config.append(new_data)
            self.populate_script_list()
            logging.info(f"Added new script '{new_data['id']}' to configuration.")

    def edit_script(self):
        selected_item = self.script_list_widget.selectedItems()[0]
        script_id = selected_item.data(Qt.ItemDataRole.UserRole)
        script_to_edit = next((s for s in self.scripts_config if s['id'] == script_id), None)
        if not script_to_edit: return
        dialog = ScriptEditDialog(script_dir=app_settings.SCRIPT_DIR, script_data=script_to_edit, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_data()
            for i, script in enumerate(self.scripts_config):
                if script['id'] == script_id: self.scripts_config[i] = updated_data
            self.populate_script_list()
            logging.info(f"Edited script '{script_id}'.")
            
    def edit_script_file(self):
        selected_items = self.script_list_widget.selectedItems()
        if not selected_items:
            return
        script_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        script_info = next((s for s in self.scripts_config if s['id'] == script_id), None)
        if not script_info:
            QMessageBox.critical(self, "Error", "Could not find script data for the selected item.")
            return
        script_path = app_settings.SCRIPT_DIR / script_info['path']
        if not script_path.exists():
            QMessageBox.warning(self, "File Not Found", f"The script file '{script_path}' does not exist on disk.")
            return
        editor_dialog = InAppEditorDialog(script_path, self)
        editor_dialog.exec()

    def remove_script(self):
        selected_item = self.script_list_widget.selectedItems()[0]
        script_id = selected_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.warning(self, "Confirm Removal",
            f"Are you sure you want to remove the script '{script_id}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.scripts_config = [s for s in self.scripts_config if s['id'] != script_id]
            self.populate_script_list()
            logging.info(f"Removed script '{script_id}'.")

    def populate_workflow_list(self):
        self.workflow_list_widget.clear()
        for wf_id, wf_data in sorted(self.workflows_config.items()):
            item = QListWidgetItem(wf_data['name'])
            item.setData(Qt.ItemDataRole.UserRole, wf_id)
            self.workflow_list_widget.addItem(item)

    def workflow_selection_changed(self):
        self.included_scripts_widget.clear()
        self.available_scripts_widget.clear()
        selected_items = self.workflow_list_widget.selectedItems()
        
        if not selected_items:
            self.workflow_name_input.clear()
            self.workflow_desc_input.clear()
            self.update_workflow_button_states()
            return
            
        wf_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        workflow = self.workflows_config[wf_id]
        
        try:
            self.workflow_name_input.textChanged.disconnect()
            self.workflow_desc_input.textChanged.disconnect()
        except TypeError:
            pass
            
        self.workflow_name_input.setText(workflow.get('name', ''))
        self.workflow_desc_input.setText(workflow.get('description', ''))
        
        self.workflow_name_input.textChanged.connect(self.update_workflow_details)
        self.workflow_desc_input.textChanged.connect(self.update_workflow_details)

        included_ids = set(workflow.get('scripts', []))
        all_scripts_map = {s['id']: s['name'] for s in self.scripts_config}

        for script_id in workflow.get('scripts', []):
            if script_id in all_scripts_map:
                item = QListWidgetItem(f"{all_scripts_map[script_id]} ({script_id})")
                item.setData(Qt.ItemDataRole.UserRole, script_id)
                self.included_scripts_widget.addItem(item)

        for script_id, script_name in all_scripts_map.items():
            if script_id not in included_ids:
                item = QListWidgetItem(f"{script_name} ({script_id})")
                item.setData(Qt.ItemDataRole.UserRole, script_id)
                self.available_scripts_widget.addItem(item)
        
        self.update_workflow_button_states()

    def update_workflow_details(self):
        selected_items = self.workflow_list_widget.selectedItems()
        if not selected_items: return
        wf_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.workflows_config[wf_id]['name'] = self.workflow_name_input.text()
        self.workflows_config[wf_id]['description'] = self.workflow_desc_input.toPlainText()
        selected_items[0].setText(self.workflow_name_input.text())

    def update_workflow_button_states(self):
        wf_selected = len(self.workflow_list_widget.selectedItems()) > 0
        included_selected = len(self.included_scripts_widget.selectedItems()) > 0
        available_selected = len(self.available_scripts_widget.selectedItems()) > 0

        self.workflow_name_input.setEnabled(wf_selected)
        self.workflow_desc_input.setEnabled(wf_selected)
        self.remove_wf_button.setEnabled(wf_selected)
        self.add_script_to_wf_button.setEnabled(wf_selected and available_selected)
        self.remove_script_from_wf_button.setEnabled(wf_selected and included_selected)
        self.move_up_button.setEnabled(included_selected)
        self.move_down_button.setEnabled(included_selected)

    def add_script_to_workflow(self):
        selected_wf_item = self.workflow_list_widget.selectedItems()[0]
        wf_id = selected_wf_item.data(Qt.ItemDataRole.UserRole)
        for item in self.available_scripts_widget.selectedItems():
            script_id = item.data(Qt.ItemDataRole.UserRole)
            self.workflows_config[wf_id]['scripts'].append(script_id)
        self.workflow_selection_changed()

    def remove_script_from_workflow(self):
        selected_wf_item = self.workflow_list_widget.selectedItems()[0]
        wf_id = selected_wf_item.data(Qt.ItemDataRole.UserRole)
        for item in self.included_scripts_widget.selectedItems():
            script_id = item.data(Qt.ItemDataRole.UserRole)
            self.workflows_config[wf_id]['scripts'].remove(script_id)
        self.workflow_selection_changed()

    def move_script_in_workflow(self, direction):
        selected_wf_item = self.workflow_list_widget.selectedItems()[0]
        wf_id = selected_wf_item.data(Qt.ItemDataRole.UserRole)
        current_row = self.included_scripts_widget.currentRow()
        if current_row == -1: return
        new_row = current_row + direction
        if 0 <= new_row < self.included_scripts_widget.count():
            scripts = self.workflows_config[wf_id]['scripts']
            scripts.insert(new_row, scripts.pop(current_row))
            self.workflow_selection_changed()
            self.included_scripts_widget.setCurrentRow(new_row)

    def add_workflow(self):
        text, ok = QInputDialog.getText(self, 'New Workflow', 'Enter a name for the new workflow:')
        if ok and text:
            wf_id = text.lower().replace(" ", "_")
            if wf_id in self.workflows_config:
                QMessageBox.warning(self, "Error", "A workflow with this ID already exists.")
                return
            self.workflows_config[wf_id] = {"name": text, "description": "New workflow.", "scripts": []}
            self.populate_workflow_list()

    def remove_workflow(self):
        selected_item = self.workflow_list_widget.selectedItems()[0]
        wf_id = selected_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.warning(self, "Confirm Removal",
            f"Are you sure you want to remove the workflow '{self.workflows_config[wf_id]['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del self.workflows_config[wf_id]
            self.populate_workflow_list()
            self.workflow_selection_changed()

    def save_and_close(self):
        self.gather_ui_data()
        new_password = self.general_config.get('new_password')
        if new_password and new_password != self.confirm_password_input.text():
            QMessageBox.warning(self, "Password Mismatch", "The new passwords do not match. Please re-enter them.")
            return
        if save_config(self.general_config, self.scripts_config, self.workflows_config):
            QMessageBox.information(self, "Success", "Configuration saved successfully. The application may need to be restarted for some changes to take effect.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save configuration. Check the logs for details.")
