"""
Encryption utilities for secure credential storage.
"""
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""

    def __init__(self):
        """Initialize encryption service with key from settings."""
        if not settings.ENCRYPTION_KEY:
            raise ValueError(
                "ENCRYPTION_KEY not set in environment. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )

        try:
            self.fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        except Exception as e:
            raise ValueError(f"Invalid ENCRYPTION_KEY format: {str(e)}")

    def encrypt(self, plain_value: str) -> str:
        """Encrypt a plain text value.

        Args:
            plain_value: Plain text string to encrypt

        Returns:
            str: Encrypted value (base64 encoded)

        Raises:
            ValueError: If encryption fails
        """
        if not plain_value:
            raise ValueError("Cannot encrypt empty value")

        try:
            encrypted_bytes = self.fernet.encrypt(plain_value.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise ValueError(f"Encryption failed: {str(e)}")

    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt an encrypted value.

        Args:
            encrypted_value: Encrypted string (base64 encoded)

        Returns:
            str: Decrypted plain text value

        Raises:
            ValueError: If decryption fails or token is invalid
        """
        if not encrypted_value:
            raise ValueError("Cannot decrypt empty value")

        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_value.encode())
            return decrypted_bytes.decode()
        except InvalidToken:
            logger.error("Decryption failed: Invalid token or corrupted data")
            raise ValueError("Decryption failed: Invalid or corrupted encrypted value")
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise ValueError(f"Decryption failed: {str(e)}")

    def is_encrypted(self, value: str) -> bool:
        """Check if a value appears to be encrypted.

        Args:
            value: Value to check

        Returns:
            bool: True if value appears to be encrypted (Fernet format)
        """
        if not value:
            return False

        try:
            # Fernet tokens are base64 encoded and start with 'g'
            # This is a heuristic check, not definitive
            self.fernet.decrypt(value.encode())
            return True
        except Exception:
            return False


# Global instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get or create the global encryption service instance.

    Returns:
        EncryptionService: Singleton encryption service instance
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


# Convenience functions
def encrypt_value(plain_value: str) -> str:
    """Encrypt a plain text value.

    Args:
        plain_value: Plain text string to encrypt

    Returns:
        str: Encrypted value
    """
    return get_encryption_service().encrypt(plain_value)


def decrypt_value(encrypted_value: str) -> str:
    """Decrypt an encrypted value.

    Args:
        encrypted_value: Encrypted string

    Returns:
        str: Decrypted plain text value
    """
    return get_encryption_service().decrypt(encrypted_value)
