"""
Cryptographic core for blockchain encryption.
Uses AES-256-GCM for block encryption and Argon2 for key derivation.
"""

import os
import base64
import hashlib
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# Argon2 configuration (OWASP recommended)
ARGON2_TIME_COST = 3        # iterations
ARGON2_MEMORY_COST = 65536  # 64 MB
ARGON2_PARALLELISM = 4      # threads
ARGON2_HASH_LEN = 32        # output bytes
ARGON2_SALT_LEN = 16        # salt bytes

# AES-GCM configuration
AES_NONCE_LEN = 12          # 96-bit nonce recommended for GCM


class CryptoManager:
    """Handles all cryptographic operations."""

    def __init__(self):
        self.ph = PasswordHasher(
            time_cost=ARGON2_TIME_COST,
            memory_cost=ARGON2_MEMORY_COST,
            parallelism=ARGON2_PARALLELISM,
            hash_len=ARGON2_HASH_LEN,
            type=Type.ID  # Argon2id - hybrid resistant to side-channel & GPU attacks
        )
        self._master_key = None

    def derive_key(self, password: str, salt: bytes = None) -> tuple:
        """
        Derive encryption key from password using Argon2id.
        Returns (key_bytes, salt_bytes).
        """
        if salt is None:
            salt = os.urandom(ARGON2_SALT_LEN)

        # Use raw Argon2 hash for key derivation (not the phc string format)
        from argon2.low_level import hash_secret_raw

        key = hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=ARGON2_TIME_COST,
            memory_cost=ARGON2_MEMORY_COST,
            parallelism=ARGON2_PARALLELISM,
            hash_len=ARGON2_HASH_LEN,
            type=Type.ID
        )
        return key, salt

    def set_master_key(self, password: str, salt: bytes = None):
        """Derive and store master key in memory."""
        self._master_key, salt = self.derive_key(password, salt)
        return salt

    def get_master_key(self) -> bytes:
        """Get current master key."""
        if self._master_key is None:
            raise ValueError("Master key not set. Please unlock the blockchain first.")
        return self._master_key

    def clear_key(self):
        """Clear master key from memory."""
        if self._master_key:
            # Overwrite with zeros before clearing
            self._master_key = b'\x00' * len(self._master_key)
            self._master_key = None

    def encrypt(self, plaintext: bytes, key: bytes = None) -> dict:
        """
        Encrypt data using AES-256-GCM.
        Returns dict with nonce and ciphertext (both base64 encoded).
        """
        if key is None:
            key = self.get_master_key()

        aesgcm = AESGCM(key)
        nonce = os.urandom(AES_NONCE_LEN)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        return {
            'nonce': base64.b64encode(nonce).decode('ascii'),
            'ciphertext': base64.b64encode(ciphertext).decode('ascii')
        }

    def decrypt(self, nonce_b64: str, ciphertext_b64: str, key: bytes = None) -> bytes:
        """
        Decrypt data using AES-256-GCM.
        Raises exception if decryption fails (wrong key or tampered data).
        """
        if key is None:
            key = self.get_master_key()

        aesgcm = AESGCM(key)
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ciphertext_b64)

        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext

    def hash_data(self, data: bytes) -> str:
        """Create SHA-256 hash of data (hex encoded)."""
        return hashlib.sha256(data).hexdigest()

    def generate_salt(self) -> bytes:
        """Generate a new random salt."""
        return os.urandom(ARGON2_SALT_LEN)


def verify_password(password: str, salt: bytes, expected_key_b64: str) -> bool:
    """Verify password against stored key hash."""
    crypto = CryptoManager()
    derived_key, _ = crypto.derive_key(password, salt)
    expected_key = base64.b64decode(expected_key_b64)
    return derived_key == expected_key
