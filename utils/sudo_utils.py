# app/utils/sudo_utils.py
import subprocess
import time
import threading
import logging
from pathlib import Path  # <-- Add this import

def check_sudo_password(system_password: str) -> bool:
    """
    Validates the user's system password by calling `sudo -v`.
    Returns True if successful, False otherwise.
    """
    try:
        # This just verifies the password is correct by elevating once
        command = f"echo '{system_password}' | sudo -S -v"
        subprocess.run(command, shell=True, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def keep_sudo_active(system_password: str, interval: int = 240):
    """
    Periodically refreshes sudo so it doesn’t expire.
    This function should be run in a background thread.
    """
    while True:
        command = f"echo '{system_password}' | sudo -S -v"
        # We don’t need the output, so pipe it to avoid printing on screen
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(interval)

def run_script_as_sudo(script_path: Path, system_password: str) -> bool:
    """
    Runs the given script with sudo privileges.
    You only need the password if the session isn't kept alive,
    but passing it won't hurt if it's valid.
    """
    command = f"echo '{system_password}' | sudo -S bash '{script_path}'"
    try:
        completed = subprocess.run(command, shell=True, check=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("%s output:\n%s", script_path.name, completed.stdout.decode())
        return True
    except subprocess.CalledProcessError as e:
        logging.error("Script %s failed as sudo: %s", script_path.name, e.stderr.decode())
        return False

def run_script_no_sudo(script_path: Path) -> bool:
    """
    Runs script without sudo privileges.
    """
    try:
        completed = subprocess.run(["bash", str(script_path)], check=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("%s output:\n%s", script_path.name, completed.stdout.decode())
        return True
    except subprocess.CalledProcessError as e:
        logging.error("Script %s failed: %s", script_path.name, e.stderr.decode())
        return False