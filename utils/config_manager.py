# app/utils/config_manager.py

import logging
from pathlib import Path
import json
import hashlib
from pprint import pformat

try:
    from app.config import settings
    from app.config.settings_template import DEFAULT_SETTINGS_CONTENT
except ImportError as e:
    logging.error(f"Could not import settings modules: {e}")
    settings = type('module', (object,))({
        'SCRIPTS': [], 'WORKFLOWS': {}, 'APP_NAME': 'Script Weaver',
        'COMPANY_NAME': 'Default', 'MAX_LOGIN_ATTEMPTS': 3, 'PASSWORD_HASH': '',
        'LOGO_PATH': '', 'APP_VERSION': '0.0.0'
    })()
    DEFAULT_SETTINGS_CONTENT = ""

SETTINGS_FILE_PATH = Path(settings.__file__).resolve()

def load_config():
    """Loads all configurations from the settings module."""
    try:
        general_settings = {
            "APP_NAME": settings.APP_NAME,
            "COMPANY_NAME": settings.COMPANY_NAME,
            "MAX_LOGIN_ATTEMPTS": settings.MAX_LOGIN_ATTEMPTS,
            "PASSWORD_HASH": settings.PASSWORD_HASH,
            "LOGO_PATH": settings.LOGO_PATH,
            "APP_VERSION": settings.APP_VERSION
        }
        scripts = json.loads(json.dumps(settings.SCRIPTS))
        workflows = json.loads(json.dumps(settings.WORKFLOWS))
        return general_settings, scripts, workflows
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return {}, [], {}

def save_config(general_settings: dict, scripts_data: list, workflows_data: dict):
    """Safely saves all updated configurations by completely rewriting the settings.py file."""
    try:
        if 'new_password' in general_settings and general_settings['new_password']:
            new_pass = general_settings.pop('new_password')
            general_settings['PASSWORD_HASH'] = hashlib.sha256(new_pass.encode()).hexdigest()

        # Use pformat to generate valid Python code for the data structures
        scripts_str = pformat(scripts_data, indent=4)
        workflows_str = pformat(workflows_data, indent=4)

        content = [
            "# app/config/settings.py\n\n",
            "import os\n", "import sys\n", "import logging\n",
            "from datetime import datetime\n", "from pathlib import Path\n\n",
            "# ------------------------------------------------------------------\n",
            "# Application settings\n",
            "# ------------------------------------------------------------------\n",
            f'APP_NAME = {json.dumps(general_settings.get("APP_NAME", "Script Weaver"))}\n',
            f'APP_VERSION = {json.dumps(general_settings.get("APP_VERSION", "1.0.0"))}\n',
            f'COMPANY_NAME = {json.dumps(general_settings.get("COMPANY_NAME", "Default"))}\n',
            f'LOGO_PATH = {json.dumps(general_settings.get("LOGO_PATH", ""))}\n',
            f'MAX_LOGIN_ATTEMPTS = {general_settings.get("MAX_LOGIN_ATTEMPTS", 3)}\n\n',
            "# ------------------------------------------------------------------\n",
            "# Paths\n", "# ------------------------------------------------------------------\n",
            "if getattr(sys, 'frozen', False):\n",
            "    APP_DIR = Path(sys.executable).parent\n", "else:\n",
            "    APP_DIR = Path(__file__).parent.parent\n\n",
            'SCRIPT_DIR = APP_DIR / "scripts"\n',
            'ASSETS_DIR = APP_DIR / "assets"\n',
            "LOG_DIR = Path.home() / 'Library' / 'Logs' / 'ScriptWeaver'\n",
            "DATA_DIR = Path.home() / 'Library' / 'Application Support' / 'ScriptWeaver'\n\n",
            "# Create necessary directories\n",
            "LOG_DIR.mkdir(parents=True, exist_ok=True)\n",
            "DATA_DIR.mkdir(parents=True, exist_ok=True)\n",
            "ASSETS_DIR.mkdir(parents=True, exist_ok=True)\n\n",
            "# ------------------------------------------------------------------\n",
            "# Script definitions\n", "# ------------------------------------------------------------------\n",
            f"SCRIPTS = {scripts_str}\n\n",
            "# ------------------------------------------------------------------\n",
            "# Workflow Definitions\n", "# ------------------------------------------------------------------\n",
            f"WORKFLOWS = {workflows_str}\n\n",
            "# ------------------------------------------------------------------\n",
            "# Security settings\n", "# ------------------------------------------------------------------\n",
            f'PASSWORD_HASH = {json.dumps(general_settings["PASSWORD_HASH"])}\n\n',
            "# ------------------------------------------------------------------\n",
            "# Logging\n", "# ------------------------------------------------------------------\n",
            "def setup_logging():\n",
            "    log_file = LOG_DIR / f'script_weaver_{datetime.now():%Y%m%d}.log'\n",
            "    logging.basicConfig(\n",
            "        level=logging.DEBUG,\n",
            "        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',\n",
            "        handlers=[\n",
            "            logging.FileHandler(log_file),\n",
            "            logging.StreamHandler(sys.stdout)\n", "        ]\n", "    )\n\n",
            "if 'pytest' not in sys.modules:\n", "    setup_logging()\n"
        ]

        with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(content)
            
        logging.info(f"Successfully saved and rewrote configuration to {SETTINGS_FILE_PATH}")
        return True

    except Exception as e:
        logging.error(f"Failed to save configuration: {e}", exc_info=True)
        return False

def reset_to_defaults():
    """Overwrites the current settings.py with a default template."""
    try:
        with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(DEFAULT_SETTINGS_CONTENT)
        logging.info("Application settings have been reset to default.")
        return True
    except Exception as e:
        logging.error(f"Failed to reset settings to default: {e}", exc_info=True)
        return False
