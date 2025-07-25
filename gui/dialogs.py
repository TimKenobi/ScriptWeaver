# app/gui/dialogs.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from app.config import settings

class PasswordDialog(QDialog):
    """Dialog for the 'application-level' password."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Authentication Required")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.password_label = QLabel("Enter Admin Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.accept)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(button_box)

    def get_password(self):
        return self.password_input.text()

class SystemPasswordDialog(QDialog):
    """Dialog to prompt for the macOS system password once."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Privileges Required")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel(
            "Enter your macOS system password to allow administrative scripts to run "
            "without repeated prompts."
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        self.system_password_label = QLabel("macOS System Password:")
        self.system_password_input = QLineEdit()
        self.system_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.system_password_input.returnPressed.connect(self.accept)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(self.system_password_label)
        layout.addWidget(self.system_password_input)
        layout.addWidget(button_box)

    def get_system_password(self):
        return self.system_password_input.text()

class AboutDialog(QDialog):
    """A simple dialog to display application information."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {settings.APP_NAME}")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(settings.APP_NAME)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        version_label = QLabel(f"Version: {settings.APP_VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        company_label = QLabel(f"Company: {settings.COMPANY_NAME}")
        company_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(company_label)
        layout.addSpacing(20)
        layout.addWidget(ok_button)
