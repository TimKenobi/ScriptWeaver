# app/core/security.py

import hashlib
import logging
from datetime import datetime, timedelta
from app.config.settings import PASSWORD_HASH, MAX_LOGIN_ATTEMPTS

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self.login_attempts = 0
        self.last_attempt = None
        self.locked_until = None

    def verify_password(self, password: str) -> bool:
        """Verify password and manage login attempts"""
        if self.is_locked():
            return False

        self.last_attempt = datetime.now()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if password_hash == PASSWORD_HASH:
            self.login_attempts = 0
            return True

        self.login_attempts += 1
        if self.login_attempts >= MAX_LOGIN_ATTEMPTS:
            self.locked_until = datetime.now() + timedelta(minutes=15)
            logger.warning(f"Account locked due to too many failed attempts")

        return False

    def is_locked(self) -> bool:
        """Check if login is locked due to too many attempts"""
        if self.locked_until and datetime.now() < self.locked_until:
            return True
        if self.locked_until and datetime.now() >= self.locked_until:
            self.locked_until = None
            self.login_attempts = 0
        return False

    def get_lockout_message(self) -> str:
        """Get message about lockout status"""
        if self.is_locked():
            remaining = self.locked_until - datetime.now()
            return f"Account is locked. Try again in {remaining.seconds // 60} minutes"
        return ""