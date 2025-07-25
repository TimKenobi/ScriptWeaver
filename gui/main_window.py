# main_window.py

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QDialog,
    QProgressDialog, QApplication, QTabWidget, QGridLayout, QToolBar
)
from PyQt6.QtGui import QIcon, QAction  # Corrected import for QAction
from PyQt6.QtCore import Qt
import logging
import sys
import time
from pathlib import Path
from hashlib import sha256
import threading
import webbrowser

# Import your custom dialogs
from app.gui.dialogs import PasswordDialog, SystemPasswordDialog
# Import your settings
from app.config.settings import SCRIPTS, PASSWORD_HASH, MAX_LOGIN_ATTEMPTS, setup_logging

# Initialize logging
setup_logging()

# Import the sudo utilities
from app.utils.sudo_utils import (
    check_sudo_password, keep_sudo_active,
    run_script_as_sudo, run_script_no_sudo
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.info("Initializing main window")
        self.setWindowTitle("Script Weaver")

        # 1) Authenticate at the application level (your existing password check)
        if not self.authenticate():
            logging.info("Authentication failed, closing application")
            sys.exit()

        # 2) Prompt for the system (macOS) password once
        if not self.authenticate_system_password():
            # If user cancels or fails, exit
            logging.info("Failed to get a valid system password, closing app")
            sys.exit()

        # Now we have self.system_password containing the valid macOS password
        # We keep the sudo session alive in the background to avoid timeouts
        self.start_sudo_keep_alive()

        self.setup_ui()

        # Make the window resizable and set a smaller initial size
        self.setMinimumSize(800, 600)
        self.resize(800, 600)

    def setup_ui(self):
        logging.debug("Setting up UI")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        welcome_label = QLabel("Welcome to Script Weaver!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)

        # Button for Install Company Portal (includes description in pop-up):
        install_company_portal_button = QPushButton("Install Company Portal")
        script_info = next((s for s in SCRIPTS if s['id'] == 'install_company_portal'), None)
        desc = script_info['description'] if script_info else ""
        install_company_portal_button.clicked.connect(
            lambda: self.confirm_and_run(self.run_install_company_portal, desc)
        )
        layout.addWidget(install_company_portal_button)

        # Example: New Setup buttons
        buttons_layout = QHBoxLayout()
        self.add_script_button(buttons_layout, "New Setup", self.run_new_setup, "Runs the new setup scripts")
        layout.addLayout(buttons_layout)

        # Advanced Features button
        self.advanced_button = QPushButton("Advanced Features")
        self.advanced_button.clicked.connect(self.toggle_advanced_features)
        layout.addWidget(self.advanced_button)

        # Advanced features layout
        self.advanced_widget = QWidget()
        self.advanced_layout = QVBoxLayout(self.advanced_widget)
        self.advanced_tabs = QTabWidget()
        self.advanced_tabs.addTab(self.create_tab_content('Tools'), "Tools")
        self.advanced_tabs.addTab(self.create_tab_content('Configuration'), "Configuration")
        self.advanced_tabs.addTab(self.create_tab_content('Software'), "Software")
        self.advanced_layout.addWidget(self.advanced_tabs)
        self.advanced_widget.setVisible(False)  # Initially hidden
        layout.addWidget(self.advanced_widget)

        self.setMinimumSize(1200,1000)

        # Add info icon to the toolbar
        self.add_info_icon()

    def add_info_icon(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        info_action = QAction(QIcon.fromTheme("help-about"), "Info", self)
        info_action.triggered.connect(self.open_info_link)
        toolbar.addAction(info_action)

    def open_info_link(self):
        webbrowser.open("https://github.com/TimKenobi/Script_Weaver/")

    def run_install_company_portal(self):
        """Run the Install Company Portal script."""
        self.run_script_by_id('companyportal')

    def add_script_button(self, layout, name, callback, description=""):
        """
        Example wrapper to add a button that triggers confirm_and_run with a description.
        """
        button = QPushButton(name)
        button.clicked.connect(lambda: self.confirm_and_run(callback, description))
        layout.addWidget(button)

    def confirm_and_run(self, script_function, script_description=""):
        """
        Generic confirmation pop-up that includes the script’s description.
        """
        message = f"Are you sure you want to run this script?\n\n{script_description}"
        reply = QMessageBox.question(
            self,
            'Confirmation',
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            script_function()

    def toggle_advanced_features(self):
        self.advanced_widget.setVisible(not self.advanced_widget.isVisible())
        if self.advanced_widget.isVisible():
            self.advanced_button.setText("Hide Advanced Features")
        else:
            self.advanced_button.setText("Advanced Features")

    def create_tab_content(self, category):
        tab_content = QWidget()
        layout = QGridLayout(tab_content)

        scripts = [s for s in SCRIPTS if s['category'] == category]
        for i, script in enumerate(scripts):
            button = QPushButton(script['name'])
            button.setToolTip(script['description'])
            button.clicked.connect(
                lambda _, s=script: self.confirm_and_run(
                    lambda: self.run_script_by_id(s['id']),
                    s['description']
                )
            )
            layout.addWidget(button, i // 4, i % 4)  # Adjust the 4 to change columns

        return tab_content

    def authenticate(self):
        """Your existing app-level password check using sha256."""
        logging.debug("Starting authentication")
        attempts = 0

        while attempts < MAX_LOGIN_ATTEMPTS:
            dialog = PasswordDialog(self)
            result = dialog.exec()

            if result != QDialog.DialogCode.Accepted:
                logging.info("Authentication cancelled by user")
                return False

            password = dialog.get_password()
            entered_hash = sha256(password.encode()).hexdigest()

            if entered_hash != PASSWORD_HASH:
                attempts += 1
                remaining = MAX_LOGIN_ATTEMPTS - attempts
                logging.warning(f"Invalid password attempt {attempts}/{MAX_LOGIN_ATTEMPTS}")
                if remaining > 0:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Invalid password. {remaining} attempts remaining."
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Maximum login attempts reached. Application will close."
                    )
                    self.open_web_link_on_fail()
                    return False
            else:
                logging.info("App-level authentication succeeded")
                return True

        return False

    def authenticate_system_password(self) -> bool:
        """
        Prompts for the macOS system password, checks it with sudo -v,
        and returns True if valid. Stores password in self.system_password.
        """
        dialog = SystemPasswordDialog(self)
        result = dialog.exec()
        if result != QDialog.DialogCode.Accepted:
            return False  # user canceled

        self.system_password = dialog.get_system_password()
        if not self.system_password:
            return False

        # Check if it's valid for sudo
        if not check_sudo_password(self.system_password):
            QMessageBox.critical(
                self,
                "Error",
                "Invalid macOS system password. Cannot proceed."
            )
            return False

        logging.info("System-level (sudo) password authenticated successfully")
        return True

    def start_sudo_keep_alive(self):
        """
        Spawns a background thread to periodically call sudo -v
        so the session doesn’t expire.
        """
        self.keep_alive_thread = threading.Thread(
            target=keep_sudo_active,
            args=(self.system_password, 240),  # refresh every 4 minutes
            daemon=True
        )
        self.keep_alive_thread.start()

    def run_new_setup(self):
        """Example of running multiple scripts for 'New' setup."""
        new_scripts = ['default_apps', 'teams', 'install_office', 'companyportal', 'vpnkeepalive', 'run_updates']  # Just an example
        self.run_multiple_scripts(new_scripts, "New Setup")

    def run_multiple_scripts(self, script_ids, setup_name):
        """
        Iterates through a sub-list of script IDs. For each script:
          - Looks up the script in SCRIPTS
          - Calls self.run_script(...)
          - Updates a QProgressDialog
        """
        progress_steps = len(script_ids) * 10  # arbitrary scale
        progress = QProgressDialog(f"Running {setup_name}...", "Cancel", 0, progress_steps, self)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()

        all_successful = True
        for idx, script_id in enumerate(script_ids, 1):
            if progress.wasCanceled():
                break

            script = next((s for s in SCRIPTS if s['id'] == script_id), None)
            if script:
                success = self.run_script(script['name'], script['path'])
                if not success:
                    all_successful = False
                    if not self.show_error_and_continue(script['name'], "Script execution failed"):
                        break
            else:
                logging.error(f"Script with ID '{script_id}' not found for {setup_name}")
                all_successful = False
                if not self.show_error_and_continue(setup_name, "Script not found"):
                    break

            progress.setValue(idx * 10)
            QApplication.processEvents()

        progress.close()

        if not all_successful:
            QMessageBox.warning(
                self,
                "Warning",
                f"{setup_name} completed with errors. Check the logs for details."
            )
        else:
            QMessageBox.information(
                self,
                "Success",
                f"{setup_name} completed successfully."
            )

    def run_script(self, script_name, script_path):
        """
        Looks up the script, checks if it needs sudo or not,
        and runs it accordingly. Uses the sudo_utils methods.
        """
        logging.info(f"Attempting to run {script_name}")
        progress = QProgressDialog(f"Running {script_name}...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setMinimumDuration(0)  # Show immediately
        progress.setValue(0)
        progress.show()

        try:
            # Construct the full path. Adjust if your real structure is different.
            script_full_path = Path(__file__).parent.parent / 'scripts' / Path(script_path).name
            logging.debug(f"Script path: {script_full_path}")

            if not script_full_path.exists():
                raise FileNotFoundError(f"Script not found: {script_full_path}")

            # Check if the script needs sudo
            script_info = next((s for s in SCRIPTS if s['path'] == script_path), None)
            needs_sudo = script_info.get('needs_sudo', False) if script_info else False

            # Run the script
            if needs_sudo:
                success = run_script_as_sudo(script_full_path, self.system_password)
            else:
                success = run_script_no_sudo(script_full_path)

            # Simulate progress
            for i in range(1, 101, 10):
                if progress.wasCanceled():
                    logging.info(f"Script {script_name} was cancelled by user.")
                    return False
                progress.setValue(i)
                time.sleep(0.05)
                QApplication.processEvents()

            progress.close()
            return success

        except Exception as e:
            progress.close()
            logging.error(f"Error running {script_name}: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to run {script_name}:\n{str(e)}")
            return False

    def show_error_and_continue(self, item_name, error_type):
        error_message = f"{item_name} - {error_type}. Would you like to continue with the next script?"
        response = QMessageBox.warning(
            self,
            "Error Detected",
            error_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return (response == QMessageBox.StandardButton.Yes)

    def run_script_by_id(self, script_id):
        script = next((s for s in SCRIPTS if s['id'] == script_id), None)
        if script:
            self.run_script(script['name'], script['path'])
        else:
            logging.error(f"Script with ID '{script_id}' not found")
            QMessageBox.critical(self, "Error", f"Script not found with ID: {script_id}")

    def open_web_link_on_fail(self):
        # If you like, open a help link or your website upon user lockout
        import webbrowser
        webbrowser.open("https://markhjorth.github.io/nedry/")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
