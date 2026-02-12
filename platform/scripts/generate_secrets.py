#!/usr/bin/env python3
"""Генерация криптографически стойких секретов для .env"""

import base64
import secrets

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_rsa_key_pair():
    """Генерирует пару RSA-ключей для RS256 JWT."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return private_pem, public_pem


def main():
    # Случайные пароли для БД
    print(f"DB_PASSWORD={secrets.token_urlsafe(32)}")
    print(f"CLICKHOUSE_PASSWORD={secrets.token_urlsafe(32)}")
    print(f"MINIO_ROOT_PASSWORD={secrets.token_urlsafe(32)}")
    print(f"SECRET_KEY={secrets.token_hex(64)}")
    print(f"GRAFANA_PASSWORD={secrets.token_urlsafe(16)}")
    print(f"PGADMIN_PASSWORD={secrets.token_urlsafe(16)}")

    # RSA ключи для JWT
    private_pem, public_pem = generate_rsa_key_pair()
    # Кодируем в base64 для удобства хранения в .env
    private_b64 = base64.b64encode(private_pem.encode()).decode()
    public_b64  = base64.b64encode(public_pem.encode()).decode()
    print(f"JWT_PRIVATE_KEY={private_b64}")
    print(f"JWT_PUBLIC_KEY={public_b64}")

if __name__ == "__main__":
    main()