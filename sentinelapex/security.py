import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet

class SecurityManager:
    """
    Manages the encryption and decryption of sensitive data (API Keys).
    
    Uses Fernet symmetric encryption. A master key is generated once and stored
    in the user's home directory (.sentinelapex/master.key). This key is used
    to encrypt/decrypt values stored in the local .env file.
    """

    def __init__(self):
        self.config_dir = Path.home() / ".sentinelapex"
        self.key_file = self.config_dir / "master.key"
        self._ensure_master_key_exists()

    def _ensure_master_key_exists(self):
        """
        Creates the configuration directory and generates a master encryption key
        if one does not already exist.
        """
        # Create directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate key if missing
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Secure the key file permissions (Owner read/write only)
            # Note: os.chmod might not work as expected on all Windows systems,
            # but it's best practice for Unix/macOS.
            try:
                os.chmod(self.key_file, 0o600)
            except Exception:
                pass # Ignore permission errors on Windows if necessary

    def _get_fernet_instance(self) -> Fernet:
        """
        Reads the master key from disk and returns a Fernet instance.
        """
        try:
            with open(self.key_file, 'rb') as f:
                key = f.read()
            return Fernet(key)
        except Exception as e:
            raise RuntimeError(f"Failed to load security key: {e}")

    def encrypt_token(self, token: str) -> str:
        """
        Encrypts a string token (API Key).
        
        Args:
            token: The plain text API key.
            
        Returns:
            A URL-safe base64 encoded encrypted string.
        """
        if not token:
            return ""
        
        fernet = self._get_fernet_instance()
        encrypted_bytes = fernet.encrypt(token.encode('utf-8'))
        # Convert bytes to base64 string for storage in .env
        return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')

    def decrypt_token(self, token: str) -> str:
        """
        Decrypts an encrypted token string.
        
        Args:
            token: The encrypted base64 string.
            
        Returns:
            The original plain text API key, or empty string if invalid.
        """
        if not token:
            return ""
        
        try:
            fernet = self._get_fernet_instance()
            # Decode base64 string back to bytes
            encrypted_bytes = base64.urlsafe_b64decode(token.encode('utf-8'))
            # Decrypt
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception:
            # If decryption fails (wrong key, corrupted data), return empty
            return ""

    def mask_key(self, key: str) -> str:
        """
        Masks an API key for safe display in the terminal.
        Shows first 4 and last 4 characters.
        
        Args:
            key: The plain text API key.
            
        Returns:
            A masked string (e.g., "sk-p...xyz1")
        """
        if not key:
            return "Not Set"
        if len(key) < 8:
            return "****"
        return f"{key[:4]}...{key[-4:]}"