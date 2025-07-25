# app/config/settings_template.py

# This file contains the default configuration for the application.
# It is used by the 'reset_to_defaults' function in the config_manager.

DEFAULT_SETTINGS_CONTENT = """# app/config/settings.py

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# ------------------------------------------------------------------
# Application settings
# ------------------------------------------------------------------
APP_NAME = "Script Weaver"
APP_VERSION = "1.0.0"
COMPANY_NAME = "My Company"
LOGO_PATH = "" # Default logo path relative to APP_DIR
MAX_LOGIN_ATTEMPTS = 3

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent.parent

SCRIPT_DIR = APP_DIR / "scripts"
ASSETS_DIR = APP_DIR / "assets"
LOG_DIR = Path.home() / 'Library' / 'Logs' / 'ScriptWeaver'
DATA_DIR = Path.home() / 'Library' / 'Application Support' / 'ScriptWeaver'

# Create necessary directories
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# Script definitions
# ------------------------------------------------------------------
SCRIPTS = []

# ------------------------------------------------------------------
# Workflow Definitions
# ------------------------------------------------------------------
WORKFLOWS = {}

# ------------------------------------------------------------------
# Security settings
# ------------------------------------------------------------------
# This is the default hash that triggers the first-run setup wizard.
PASSWORD_HASH = "e7cf3ef4f17c3999a94f2c6f612e8a888e5b1026878e4e19398b23bd38ec221a"

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
def setup_logging():
    log_file = LOG_DIR / f'script_weaver_{{datetime.now():%Y%m%d}}.log'
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

if 'pytest' not in sys.modules:
    setup_logging()
"""
