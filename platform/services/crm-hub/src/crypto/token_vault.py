import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _derive_key(secret: str) -> bytes:
    """Из SECRET_KEY (строка) → 32-байтовый Fernet-ключ через PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"algorithmic-arts-crm",  # фиксированная соль (не секрет)
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode()))


class TokenVault:
    """
    Шифрование/дешифрование OAuth-токенов через Fernet (AES-256-CBC + HMAC-SHA256).
    Ключ берётся из SECRET_KEY в .env.
    """

    def __init__(self, secret_key: str):
        self._fernet = Fernet(_derive_key(secret_key))

    def encrypt(self, token: str) -> str:
        """Зашифровать токен → base64-строка для хранения в БД."""
        return self._fernet.encrypt(token.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        """Расшифровать токен из БД."""
        return self._fernet.decrypt(encrypted.encode()).decode()

    def rotate_key(self, old_secret: str, new_secret: str, encrypted: str) -> str:
        """
        Перешифровать токен при ротации ключа.
        Используется в migration-скрипте.
        """
        old_vault = TokenVault(old_secret)
        plaintext = old_vault.decrypt(encrypted)
        return self.encrypt(plaintext)
