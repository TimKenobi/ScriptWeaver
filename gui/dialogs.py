# dialogs.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt


class PasswordDialog(QDialog):
    """
    Dialog for your 'application-level' password.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Authentication Required")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Password input
        self.password_label = QLabel("Enter Admin Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.accept)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def get_password(self):
        return self.password_input.text()


class ScriptDialog(QDialog):
    """
    Dialog that confirms whether the user wants to run a script.
    """
    def __init__(self, script_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Run {script_name}")
        self.setModal(True)
        self.setup_ui(script_name)

    def setup_ui(self, script_name):
        layout = QVBoxLayout()

        # Confirmation message
        message = QLabel(f"Are you sure you want to run {script_name}?")
        layout.addWidget(message)

        # Buttons
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        layout.addWidget(self.run_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)


class SystemPasswordDialog(QDialog):
    """
    Dialog to prompt for the macOS system password exactly once.
    You can call this after the user is authenticated at the app level,
    to allow all subsequent scripts to run without repeated sudo prompts.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Password")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Explanation label
        label = QLabel(
            "Enter your macOS system password to allow root-level tasks.\n"
            "This is required to run administrative scripts without repeated prompts."
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        # Password input
        self.system_password_label = QLabel("macOS System Password:")
        self.system_password_input = QLineEdit()
        self.system_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # OK/Cancel
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        layout.addWidget(self.system_password_label)
        layout.addWidget(self.system_password_input)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def get_system_password(self):
        return self.system_password_input.text()
