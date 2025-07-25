# app/gui/main_window.py

import sys
import logging
from pathlib import Path
from hashlib import sha256
import importlib
import webbrowser

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QDialog, QTabWidget, QGridLayout, QToolBar, QLineEdit,
    QApplication
)
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt, QSize

from app.config import settings
from app.gui.dialogs import PasswordDialog, SystemPasswordDialog, AboutDialog
from app.gui.script_output_dialog import ScriptOutputDialog
from app.gui.settings_window import SettingsWindow
from app.utils.sudo_utils import check_sudo_password, keep_sudo_active
from app.utils.script_runner import ScriptRunner
from app.utils.file_utils import audit_script_files

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.info("Initializing main window")
        self.setWindowTitle(settings.APP_NAME)
        self.setWindowIcon(QIcon.fromTheme("system-run"))
        self._auth_success = False

        if not self.authenticate():
            logging.warning("Application-level authentication failed. Exiting.")
            return

        if not self.authenticate_system_password():
            logging.warning("System-level authentication failed. Exiting.")
            return

        self._auth_success = True
        self.start_sudo_keep_alive()
        self.setup_ui()
        self.resize(1000, 800)
        
        self.perform_script_audit()
        
        logging.info("Main window initialized successfully.")

    def is_auth_successful(self):
        return self._auth_success

    def setup_ui(self):
        logging.debug("Setting up UI")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.add_toolbar_actions()

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_logo()
        main_layout.addWidget(self.logo_label)

        welcome_label = QLabel(f"Welcome to {settings.APP_NAME}!")
        welcome_label.setObjectName("WelcomeLabel")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(welcome_label)

        self.workflow_buttons_container = QWidget()
        main_layout.addWidget(self.workflow_buttons_container)
        self.setup_workflow_buttons()

        self.advanced_button = QPushButton("Show Advanced Features")
        self.advanced_button.clicked.connect(self.toggle_advanced_features)
        main_layout.addWidget(self.advanced_button)

        self.advanced_widget = QWidget()
        advanced_layout = QVBoxLayout(self.advanced_widget)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filter scripts by name or description...")
        self.search_bar.textChanged.connect(self.filter_scripts)
        search_layout.addWidget(self.search_bar)
        advanced_layout.addLayout(search_layout)

        self.script_tabs = QTabWidget()
        self.populate_script_tabs()
        advanced_layout.addWidget(self.script_tabs)

        self.advanced_widget.setVisible(False)
        main_layout.addWidget(self.advanced_widget)
        main_layout.addStretch()

    def load_logo(self):
        if hasattr(settings, 'LOGO_PATH') and settings.LOGO_PATH:
            logo_path = settings.APP_DIR / settings.LOGO_PATH
            if logo_path.exists():
                pixmap = QPixmap(str(logo_path))
                self.logo_label.setPixmap(pixmap.scaled(256, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                logging.warning(f"Logo file not found at: {logo_path}")
                self.logo_label.clear()
        else:
            self.logo_label.clear()

    def add_toolbar_actions(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        
        about_action = QAction(QIcon.fromTheme("help-about"), "About...", self)
        about_action.triggered.connect(self.open_about_dialog)
        toolbar.addAction(about_action)

        help_action = QAction(QIcon.fromTheme("help-faq"), "Online Help", self)
        help_action.triggered.connect(self.open_info_link)
        toolbar.addAction(help_action)
        
        toolbar.addSeparator()
        
        settings_action = QAction(QIcon.fromTheme("document-properties"), "Settings...", self)
        settings_action.triggered.connect(self.open_settings_window)
        toolbar.addAction(settings_action)

    def open_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def open_settings_window(self):
        dialog = SettingsWindow(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            logging.info("Settings were changed. Reloading configuration and UI.")
            importlib.reload(settings)
            self.setWindowTitle(settings.APP_NAME)
            self.load_logo()
            self.populate_script_tabs()
            self.setup_workflow_buttons()

    def populate_script_tabs(self):
        self.script_tabs.clear()
        all_categories = sorted(list(set(s['category'] for s in settings.SCRIPTS)))
        self.tab_widgets = {}

        for category in all_categories:
            is_uninstaller_category = category.lower() == 'uninstall'
            if is_uninstaller_category and all(self.is_linked_uninstaller(s['id']) for s in settings.SCRIPTS if s['category'] == category):
                continue

            tab_content = QWidget()
            layout = QGridLayout(tab_content)
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.tab_widgets[category] = {'widget': tab_content, 'layout': layout, 'cell_widgets': []}
            self.script_tabs.addTab(tab_content, category.capitalize())

        for script in sorted(settings.SCRIPTS, key=lambda s: s['name'].lower()):
            category = script['category']
            
            if category.lower() == 'uninstall' and self.is_linked_uninstaller(script['id']):
                continue

            if category not in self.tab_widgets:
                continue

            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setContentsMargins(2, 2, 2, 2)
            cell_layout.setSpacing(5)
            cell_widget.setProperty("script_id", script['id'])

            button = QPushButton(script['name'])
            button.setToolTip(script['description'])
            button.clicked.connect(lambda _, s=script: self.confirm_and_run_script(s))
            cell_layout.addWidget(button)

            if script.get('category', '').lower() == 'software' and script.get('uninstall_id'):
                uninstall_script = self.get_script_by_id(script['uninstall_id'])
                if uninstall_script:
                    uninstall_button = QPushButton()
                    uninstall_button.setIcon(QIcon.fromTheme("edit-delete"))
                    uninstall_button.setToolTip(f"Uninstall: {uninstall_script['name']}\n{uninstall_script['description']}")
                    uninstall_button.setFixedWidth(35)
                    uninstall_button.clicked.connect(lambda _, s=uninstall_script: self.confirm_and_run_script(s))
                    cell_layout.addWidget(uninstall_button)

            cell_list = self.tab_widgets[category]['cell_widgets']
            row, col = divmod(len(cell_list), 3)
            self.tab_widgets[category]['layout'].addWidget(cell_widget, row, col)
            cell_list.append(cell_widget)

    def is_linked_uninstaller(self, script_id):
        return any(script_id == s.get('uninstall_id') for s in settings.SCRIPTS if 'uninstall_id' in s)

    def filter_scripts(self):
        filter_text = self.search_bar.text().lower()
        for category, data in self.tab_widgets.items():
            for cell_widget in data['cell_widgets']:
                script_id = cell_widget.property("script_id")
                script = self.get_script_by_id(script_id)
                if not script: continue
                matches_name = filter_text in script['name'].lower()
                matches_desc = filter_text in script['description'].lower()
                cell_widget.setVisible(matches_name or matches_desc)

    def setup_workflow_buttons(self):
        if self.workflow_buttons_container.layout() is not None:
            old_layout = self.workflow_buttons_container.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            import sip
            sip.delete(old_layout)

        workflow_layout = QHBoxLayout(self.workflow_buttons_container)
        
        if not settings.WORKFLOWS:
            self.workflow_buttons_container.setVisible(False)
            return

        self.workflow_buttons_container.setVisible(True)
        for wf_id, wf_details in settings.WORKFLOWS.items():
            button = QPushButton(wf_details['name'])
            button.setToolTip(wf_details['description'])
            button.setIcon(QIcon.fromTheme("media-playlist-repeat"))
            button.setIconSize(QSize(24, 24))
            button.clicked.connect(lambda _, wid=wf_id, dets=wf_details: self.confirm_and_run_workflow(wid, dets))
            workflow_layout.addWidget(button)

    def open_info_link(self):
        webbrowser.open("https://github.com/TimKenobi?tab=overview")

    def toggle_advanced_features(self):
        is_visible = not self.advanced_widget.isVisible()
        self.advanced_widget.setVisible(is_visible)
        self.advanced_button.setText("Hide Advanced Features" if is_visible else "Show Advanced Features")

    def confirm_and_run_script(self, script_info):
        reply = QMessageBox.question(self, 'Confirmation',
            f"Are you sure you want to run this script?\n\n<b>{script_info['name']}</b>\n{script_info['description']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.run_script(script_info)

    def confirm_and_run_workflow(self, workflow_id, workflow_details):
        script_names = "\n".join([f"- {self.get_script_by_id(sid)['name']}" for sid in workflow_details['scripts'] if self.get_script_by_id(sid)])
        reply = QMessageBox.question(self, 'Confirmation',
            f"Are you sure you want to run the '{workflow_details['name']}' workflow?\n\nIt will run the following scripts in order:\n{script_names}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.run_multiple_scripts(workflow_details['scripts'], workflow_details['name'])

    def run_script(self, script_info, is_workflow_part=False):
        logging.info(f"Running script: {script_info['name']} (ID: {script_info['id']})")
        dialog = ScriptOutputDialog(f"Running: {script_info['name']}", self)
        
        # CORRECTED PATH: Use SCRIPT_DIR, not APP_DIR
        script_path = settings.SCRIPT_DIR / script_info['path']
        if not script_path.exists():
            error_msg = f"Script file not found: {script_path}"
            logging.error(error_msg)
            dialog.append_output(f"ERROR: {error_msg}\n")
            dialog.mark_as_failed()
            dialog.exec()
            return False

        runner = ScriptRunner(str(script_path), self.system_password, script_info.get('needs_sudo', False))
        runner.output_ready.connect(dialog.append_output)
        runner.finished.connect(dialog.mark_as_finished)
        
        runner.start()
        dialog.exec()
        return runner.get_success_status()

    def run_multiple_scripts(self, script_ids, workflow_name):
        logging.info(f"Starting workflow: {workflow_name}")
        dialog = ScriptOutputDialog(f"Workflow: {workflow_name}", self)
        dialog.show()
        
        total_success = True
        for i, script_id in enumerate(script_ids):
            script_info = self.get_script_by_id(script_id)
            if not script_info:
                error_msg = f"Workflow aborted: Script with ID '{script_id}' not found."
                logging.error(error_msg)
                dialog.append_output(f"\n--- ERROR ---\n{error_msg}\n")
                total_success = False
                break

            dialog.append_output(f"\n--- Starting Step {i+1}/{len(script_ids)}: {script_info['name']} ---\n")
            QApplication.processEvents()

            # CORRECTED PATH: Use SCRIPT_DIR, not APP_DIR
            script_path = settings.SCRIPT_DIR / script_info['path']
            if not script_path.exists():
                dialog.append_output(f"ERROR: Script file not found: {script_path}\n")
                success = False
            else:
                runner = ScriptRunner(str(script_path), self.system_password, script_info.get('needs_sudo', False))
                runner.output_ready.connect(dialog.append_output)
                
                runner.start()
                while not runner.isFinished():
                    QApplication.processEvents()
                success = runner.get_success_status()

            dialog.append_output(f"--- Step {i+1} {'Succeeded' if success else 'Failed'} ---\n")
            QApplication.processEvents()

            if not success:
                total_success = False
                reply = QMessageBox.warning(self, "Workflow Error",
                    f"The script '{script_info['name']}' failed. Do you want to continue with the rest of the workflow?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    break
        
        dialog.mark_as_finished(total_success)

    def get_script_by_id(self, script_id):
        return next((s for s in settings.SCRIPTS if s['id'] == script_id), None)

    def perform_script_audit(self):
        untracked, missing = audit_script_files(settings.SCRIPTS, settings.SCRIPT_DIR)
        if untracked:
            logging.warning("AUDIT: The following scripts exist in the scripts directory but are not configured in settings.py:")
            for script_file in untracked:
                logging.warning(f"  - UNTRACKED: {script_file}")
        if missing:
            logging.warning("AUDIT: The following scripts are defined in settings.py but are MISSING from the scripts directory:")
            for script_file in missing:
                logging.warning(f"  - MISSING: {script_file}")

    def closeEvent(self, event):
        logging.info("Close event triggered.")
        reply = QMessageBox.question(self, "Exit", 
            "Are you sure you want to exit?\nThis will attempt to re-enable Gatekeeper for security.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        
        if reply == QMessageBox.StandardButton.Yes:
            gatekeeper_script = self.get_script_by_id('enable_gatekeeper')
            if gatekeeper_script:
                logging.info("Running 'enable_gatekeeper' script before exiting.")
                self.run_script(gatekeeper_script)
            else:
                logging.warning("Could not find 'enable_gatekeeper' script to run on exit.")
            
            logging.info("Exiting application.")
            event.accept()
        else:
            event.ignore()

    def authenticate(self):
        attempts = 0
        while attempts < settings.MAX_LOGIN_ATTEMPTS:
            dialog = PasswordDialog(self)
            if dialog.exec() != QDialog.DialogCode.Accepted: return False
            entered_hash = sha256(dialog.get_password().encode()).hexdigest()
            if entered_hash == settings.PASSWORD_HASH:
                logging.info("App-level authentication successful.")
                return True
            attempts += 1
            remaining = settings.MAX_LOGIN_ATTEMPTS - attempts
            QMessageBox.critical(self, "Error", f"Invalid password. {remaining} attempts remaining.")
        QMessageBox.critical(self, "Error", "Maximum login attempts reached.")
        return False

    def authenticate_system_password(self):
        dialog = SystemPasswordDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted: return False
        self.system_password = dialog.get_system_password()
        if not self.system_password or not check_sudo_password(self.system_password):
            QMessageBox.critical(self, "Error", "Invalid macOS system password.")
            return False
        logging.info("System-level (sudo) password authenticated.")
        return True

    def start_sudo_keep_alive(self):
        import threading
        self.keep_alive_thread = threading.Thread(
            target=keep_sudo_active, args=(self.system_password, 240), daemon=True
        )
        self.keep_alive_thread.start()
        logging.info("Sudo keep-alive thread started.")
