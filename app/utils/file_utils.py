# app/utils/file_utils.py

import logging
from pathlib import Path
from typing import List, Tuple

def audit_script_files(scripts_config: List[dict], script_directory: Path) -> Tuple[List[str], List[str]]:
    """
    Compares scripts on disk with scripts defined in the configuration.

    Args:
        scripts_config: The list of script dictionaries from settings.py.
        script_directory: The Path object pointing to the 'scripts' folder.

    Returns:
        A tuple containing two lists:
        - untracked_scripts: Files on disk but not in config.
        - missing_scripts: Files in config but not on disk.
    """
    if not script_directory.is_dir():
        logging.error(f"Script audit failed: Directory not found at '{script_directory}'")
        return [], []

    # Get a set of all .sh filenames defined in the config
    configured_scripts = {Path(s['path']).name for s in scripts_config if 'path' in s}
    
    # Get a set of all .sh files currently in the script directory
    disk_scripts = {p.name for p in script_directory.glob('*.sh')}

    # Find scripts on disk that are not in the configuration
    untracked_scripts = sorted(list(disk_scripts - configured_scripts))
    
    # Find scripts in the configuration that are not on disk
    missing_scripts = sorted(list(configured_scripts - disk_scripts))
    
    return untracked_scripts, missing_scripts
