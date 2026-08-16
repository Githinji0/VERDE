import base64
import hashlib
import os
import secrets
from typing import Optional
from cryptography.fernet import Fernet
from backend.app.config import settings


def _derive_fernet_key(passphrase: str) -> bytes:
    """Derive a URL-safe base64-encoded 32-byte key from passphrase."""
    digest = hashlib.sha256(passphrase.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


class SecretVault:
    """Provides secure encryption and decryption for API keys and BRAIN credentials."""

    def __init__(self, master_key: Optional[str] = None):
        key = master_key or settings.SECRET_KEY
        self.fernet = Fernet(_derive_fernet_key(key))

    def encrypt(self, plain_text: str) -> str:
        if not plain_text:
            return ""
        return self.fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")

    def decrypt(self, cipher_text: str) -> str:
        if not cipher_text:
            return ""
        try:
            return self.fernet.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
        except Exception:
            return ""


vault = SecretVault()


def hash_token(token: str) -> str:
    """Hash a token with SHA-256 for secure lookup."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_hex(length)
