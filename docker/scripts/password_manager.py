#!/usr/bin/env python3

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class PasswordManager:
    """Simple password encryption/decryption for MailDocker config"""
    
    def __init__(self, master_key=None):
        if master_key:
            self.key = self._derive_key(master_key)
        else:
            # Use environment variable or generate a default key
            key_env = os.environ.get('MAILDOCKER_KEY')
            if key_env:
                self.key = self._derive_key(key_env)
            else:
                # Default key (not super secure, but better than plain text)
                self.key = self._derive_key('mail-bridge-default-key')
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        salt = b'mail-bridge-salt-2024'  # Fixed salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, password: str) -> str:
        """Encrypt password and return base64 encoded string"""
        f = Fernet(self.key)
        encrypted = f.encrypt(password.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_password: str) -> str:
        """Decrypt base64 encoded password string"""
        try:
            f = Fernet(self.key)
            encrypted = base64.urlsafe_b64decode(encrypted_password.encode())
            decrypted = f.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt password: {e}")
    
    @staticmethod
    def generate_key() -> str:
        """Generate a random encryption key"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()

# Test the password manager
if __name__ == "__main__":
    pm = PasswordManager("test-key")
    
    # Test encryption/decryption
    original = "my-secret-password"
    encrypted = pm.encrypt(original)
    decrypted = pm.decrypt(encrypted)
    
    print(f"Original: {original}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Success: {original == decrypted}")
