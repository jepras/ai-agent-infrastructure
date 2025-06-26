from cryptography.fernet import Fernet
import base64
import os
from typing import Optional


class EncryptionManager:
    def __init__(self):
        # Get encryption key from environment or generate one
        self.key = os.getenv("ENCRYPTION_KEY")
        if not self.key:
            # Generate a new key if not provided (for development)
            self.key = Fernet.generate_key()
            print(
                f"WARNING: No ENCRYPTION_KEY found. Generated new key: {self.key.decode()}"
            )

        # Ensure key is bytes
        if isinstance(self.key, str):
            self.key = self.key.encode()

        self.cipher = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64 encoded result"""
        if not data:
            return ""

        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """Decrypt base64 encoded data and return original string"""
        if not encrypted_data:
            return None

        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None

    def is_encrypted(self, data: str) -> bool:
        """Check if data appears to be encrypted"""
        try:
            base64.b64decode(data.encode())
            return True
        except:
            return False


# Global encryption manager instance
encryption_manager = EncryptionManager()
