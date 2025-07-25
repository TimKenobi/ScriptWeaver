# app/config/settings.py

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# ------------------------------------------------------------------
# Application settings
# ------------------------------------------------------------------
APP_NAME = "Script Weaver"
APP_VERSION = "4.0.0"
COMPANY_NAME = "Pixel Space Technologies LLC"
LOGO_PATH = "assets/logo.png"
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
SCRIPTS = [
    {   'category': 'Tools',
        'description': 'Keeps VPN connection alive during sleep.',
        'id': 'vpnkeepalive',
        'name': 'Run VPN Keep Alive on Sleep',
        'needs_sudo': False,
        'path': 'keep_vpn_alive.sh'},
    {   'category': 'Tools',
        'description': 'Applies common system fixes like clearing caches and '
                       'running First Aid.',
        'id': 'common_fixes',
        'name': 'Common Fixes',
        'needs_sudo': True,
        'path': 'common_fixes.sh'},
    {   'category': 'Tools',
        'description': 'Disables system Gatekeeper. Use with caution.',
        'id': 'disable_gatekeeper',
        'name': 'Disable Gatekeeper',
        'needs_sudo': True,
        'path': 'disable_gatekeeper.sh'},
    {   'category': 'Tools',
        'description': 'Enables system Gatekeeper for security.',
        'id': 'enable_gatekeeper',
        'name': 'Enable Gatekeeper',
        'needs_sudo': True,
        'path': 'enable_gatekeeper.sh'},
    {   'category': 'Tools',
        'description': 'Runs network diagnostic tools like ping and DNS '
                       'checks.',
        'id': 'network_diagnostics',
        'name': 'Network Diagnostics',
        'needs_sudo': False,
        'path': 'network_diagnostics.sh'},
    {   'category': 'Tools',
        'description': 'Launches Time Machine Backup setup.',
        'id': 'run_backup',
        'name': 'Run Backup',
        'needs_sudo': True,
        'path': 'run_backup.sh'},
    {   'category': 'Tools',
        'description': 'Runs all available updates from App Store and System.',
        'id': 'run_updates',
        'name': 'Run Updates',
        'needs_sudo': True,
        'path': 'run_updates.sh'},
    {   'category': 'Tools',
        'description': 'Displays software versions of installed applications.',
        'id': 'software_versions',
        'name': 'Show Software Versions',
        'needs_sudo': False,
        'path': 'software_versions.sh'},
    {   'category': 'Software',
        'description': 'Installs Company Portal.',
        'id': 'companyportal',
        'name': 'Install Company Portal',
        'needs_sudo': True,
        'path': 'install_company_portal.sh',
        'uninstall_id': 'uninstall_companyportal'},
    {   'category': 'Software',
        'description': 'Installs Microsoft Office 365 apps.',
        'id': 'install_office',
        'name': 'Install Office',
        'needs_sudo': True,
        'path': 'install_office.sh',
        'uninstall_id': 'uninstall_office'},
    {   'category': 'Software',
        'description': 'Installs Microsoft Remote Desktop client.',
        'id': 'install_remote_desktop',
        'name': 'Install Remote Desktop',
        'needs_sudo': True,
        'path': 'install_remote_desktop.sh',
        'uninstall_id': 'uninstall_remote_desktop'},
    {   'category': 'Software',
        'description': 'Installs Chrome, Edge, and Zoom.',
        'id': 'default_apps',
        'name': 'Install Default Apps',
        'needs_sudo': True,
        'path': 'install_default_apps.sh',
        'uninstall_id': 'uninstall_default_apps'},
    {   'category': 'Software',
        'description': 'Installs Mozilla Firefox.',
        'id': 'firefox',
        'name': 'Install Firefox',
        'needs_sudo': True,
        'path': 'install_firefox.sh',
        'uninstall_id': 'uninstall_firefox'},
    {   'category': 'Software',
        'description': 'Installs Microsoft Teams.',
        'id': 'teams',
        'name': 'Install Microsoft Teams',
        'needs_sudo': True,
        'path': 'install_teams.sh',
        'uninstall_id': 'uninstall_teams'},
    {   'category': 'Configuration',
        'description': 'Disables synchronization between work and personal One '
                       'Drive folders.',
        'id': 'one_drive_sync',
        'name': 'Disable One Drive Personal Sync',
        'needs_sudo': True,
        'path': 'disable_one_drive_personal_sync.sh'},
    {   'category': 'Uninstall',
        'description': 'Removes the Company Portal application.',
        'id': 'uninstall_companyportal',
        'name': 'Uninstall Company Portal',
        'needs_sudo': True,
        'path': 'uninstall_company_portal.sh'},
    {   'category': 'Uninstall',
        'description': 'Removes all Microsoft Office applications.',
        'id': 'uninstall_office',
        'name': 'Uninstall Office',
        'needs_sudo': True,
        'path': 'uninstall_office.sh'},
    {   'category': 'Uninstall',
        'description': 'Removes the Microsoft Remote Desktop client.',
        'id': 'uninstall_remote_desktop',
        'name': 'Uninstall Remote Desktop',
        'needs_sudo': True,
        'path': 'uninstall_remote_desktop.sh'},
    {   'category': 'Uninstall',
        'description': 'Removes Chrome, Edge, and Zoom.',
        'id': 'uninstall_default_apps',
        'name': 'Uninstall Default Apps',
        'needs_sudo': True,
        'path': 'uninstall_default_apps.sh'},
    {   'category': 'Uninstall',
        'description': 'Removes Mozilla Firefox.',
        'id': 'uninstall_firefox',
        'name': 'Uninstall Firefox',
        'needs_sudo': True,
        'path': 'uninstall_firefox.sh'},
    {   'category': 'Uninstall',
        'description': 'Removes the Microsoft Teams application.',
        'id': 'uninstall_teams',
        'name': 'Uninstall Microsoft Teams',
        'needs_sudo': True,
        'path': 'uninstall_teams.sh'}]

# ------------------------------------------------------------------
# Workflow Definitions
# ------------------------------------------------------------------
WORKFLOWS = {   'new_setup': {   'description': 'Runs all standard setup scripts for a '
                                      'new machine.',
                       'name': 'New Setup',
                       'scripts': [   'default_apps',
                                      'teams',
                                      'install_office',
                                      'companyportal',
                                      'vpnkeepalive',
                                      'run_updates']},
    'uninstall_all': {   'description': 'Removes all managed software '
                                        'applications from the machine.',
                         'name': 'Uninstall All Software',
                         'scripts': [   'uninstall_teams',
                                        'uninstall_default_apps',
                                        'uninstall_companyportal',
                                        'uninstall_office']}}

# ------------------------------------------------------------------
# Security settings
# ------------------------------------------------------------------
PASSWORD_HASH = "e7cf3ef4f17c3999a94f2c6f612e8a888e5b1026878e4e19398b23bd38ec221a" #Get this hash from generate_hash.py

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
def setup_logging():
    log_file = LOG_DIR / f'script_weaver_{datetime.now():%Y%m%d}.log'
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