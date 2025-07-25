# app/gui/setup_wizard.py

import logging
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QMessageBox, QFileDialog, QLabel, QGroupBox
)
from PyQt6.QtGui import QIcon
from app.utils.config_manager import save_config, load_config

class SetupWizard(QDialog):
    """
    A dialog for the first-time setup of the application.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("First-Time Setup Wizard")
        self.setModal(True)
        self.setMinimumWidth(500)

        self.general_config, self.scripts_config, self.workflows_config = load_config()
        self.app_dir = Path(__file__).parent.parent

        main_layout = QVBoxLayout(self)

        welcome_label = QLabel("Welcome to the Script Weaver Setup Wizard!")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(welcome_label)
        main_layout.addWidget(QLabel("Please configure the basic settings for your application."))

        branding_group = QGroupBox("Branding")
        branding_layout = QFormLayout(branding_group)
        self.app_name_input = QLineEdit(self.general_config.get("APP_NAME", "Script Weaver"))
        self.company_name_input = QLineEdit(self.general_config.get("COMPANY_NAME", "My Company"))
        self.logo_path_input = QLineEdit(self.general_config.get("LOGO_PATH", ""))
        browse_logo_button = QPushButton(QIcon.fromTheme("document-open"), "Browse...")
        browse_logo_button.clicked.connect(self.browse_for_logo)
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_path_input)
        logo_layout.addWidget(browse_logo_button)
        branding_layout.addRow("Application Name:", self.app_name_input)
        branding_layout.addRow("Company Name:", self.company_name_input)
        branding_layout.addRow("Company Logo:", logo_layout)
        main_layout.addWidget(branding_group)

        security_group = QGroupBox("Security")
        security_layout = QFormLayout(security_group)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        security_layout.addRow("New Admin Password:", self.new_password_input)
        security_layout.addRow("Confirm Password:", self.confirm_password_input)
        main_layout.addWidget(security_group)
        
        main_layout.addStretch()

        self.finish_button = QPushButton(QIcon.fromTheme("dialog-ok-apply"), "Finish Setup")
        self.finish_button.clicked.connect(self.finish_setup)
        main_layout.addWidget(self.finish_button)

    def browse_for_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Logo File", "", "Images (*.png *.jpg *.jpeg *.svg)")
        if not file_path:
            return

        source_path = Path(file_path)
        assets_dir = self.app_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        dest_filename = "logo" + source_path.suffix
        dest_path = assets_dir / dest_filename

        try:
            shutil.copy(source_path, dest_path)
            relative_path = dest_path.relative_to(self.app_dir)
            self.logo_path_input.setText(str(relative_path))
            logging.info(f"Copied new logo to {dest_path}")
        except Exception as e:
            logging.error(f"Failed to copy logo file: {e}")
            QMessageBox.critical(self, "Error", f"Could not copy logo file: {e}")

    def finish_setup(self):
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not self.app_name_input.text() or not self.company_name_input.text():
            QMessageBox.warning(self, "Missing Information", "Application Name and Company Name cannot be empty.")
            return

        if not new_password:
            QMessageBox.warning(self, "Password Required", "You must set an initial administrator password.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "The passwords do not match. Please re-enter them.")
            return

        self.general_config['APP_NAME'] = self.app_name_input.text()
        self.general_config['COMPANY_NAME'] = self.company_name_input.text()
        self.general_config['LOGO_PATH'] = self.logo_path_input.text()
        self.general_config['new_password'] = new_password

        if save_config(self.general_config, self.scripts_config, self.workflows_config):
            QMessageBox.information(self, "Setup Complete", "Initial setup is complete. The application will now close. Please restart it to continue.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save initial configuration. Please check the logs.")
