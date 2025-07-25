# app/core/script_loader.py

import base64
import zlib
import os
from cryptography.fernet import Fernet
from app.config.settings import ENCRYPTION_KEY

class ScriptLoader:
    def __init__(self):
        self.key = ENCRYPTION_KEY.encode()
        self.fernet = Fernet(self.key)

    def load_encrypted_script(self, script_id: str) -> str:
        """Load and decrypt embedded script"""
        try:
            # Get encrypted script from embedded_scripts
            encrypted_data = EMBEDDED_SCRIPTS.get(script_id)
            if notf"Script {script_id} not found")

            # Decode and decrypt
            decoded = base64.b64decode(encrypted_data)
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()

    def execute_secure_script(self, script_id: str):
        """Execute script securely"""
        script_content = self.load_encrypted_script(script_id)
        
        # Create temporary script file
        temp_path = os.path.join(os.getenv('TMPDIR', '/tmp'), f'{os.urandom(16).hex()}.sh')
        try:
            with open(temp_path, 'w') as f:
                f.write(script_content)
            os.chmod(temp_path, 0o700)  # Executable only by owner
            
            # Execute and return result
            result = subprocess.run(['bash', temp_path], 
                                 capture_output=True, 
                                 text=True)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)