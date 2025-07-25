# main.py
import sys
from pathlib import Path
import logging
from datetime import datetime
import os

def get_project_root():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent.parent

def setup_logging():
    try:
        log_dir_parent = Path.home() / 'Library' / 'Logs'
        logs_dir = log_dir_parent / 'ScriptWeaver'
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
        log_file.touch(exist_ok=True)
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(log_file)),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.info(f"Logging initialized. Log file: {log_file}")
    except Exception as e:
        print(f"Error setting up logging: {e}")

def main():
    project_root = get_project_root()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        setup_logging()
        logging.info("Starting Script Weaver application")
        logging.info(f"Project Root added to path: {project_root}")

        from PyQt6.QtWidgets import QApplication, QDialog
        from app.config import settings
        from app.gui.style import STYLESHEET
        from app.gui.setup_wizard import SetupWizard

        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        app.setStyleSheet(STYLESHEET)

        DEFAULT_HASH = "e7cf3ef4f17c3999a94f2c6f612e8a888e5b1026878e4e19398b23bd38ec221a"
        if settings.PASSWORD_HASH == DEFAULT_HASH:
            logging.info("Default password hash detected. Running first-time setup wizard.")
            wizard = SetupWizard()
            if wizard.exec() == QDialog.DialogCode.Accepted:
                sys.exit(0)
            else:
                logging.info("Setup wizard was cancelled. Exiting.")
                sys.exit(0)

        from app.gui.main_window import MainWindow
        
        logging.info("Creating main window")
        window = MainWindow()
        
        if not window.is_auth_successful():
            logging.warning("Authentication failed during initialization. Application will now exit.")
            sys.exit(1)

        window.show()
        logging.info("Application event loop started")
        sys.exit(app.exec())

    except ModuleNotFoundError as e:
        logging.error(f"Fatal ModuleNotFoundError: {e}. Check dependencies.", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logging.error(f"Fatal application error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
