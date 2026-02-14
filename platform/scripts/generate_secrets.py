#!/usr/bin/env python3
"""Generate secrets for ALGORITHMIC ARTS platform."""

import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat

def generate_jwt_keys():
    """Generate RSA key pair for JWT."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    # Serialize public key
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem

def main():
    """Main function to generate secrets."""
    print("# Generated secrets for ALGORITHMIC ARTS platform")
    print("# DO NOT COMMIT THIS FILE TO VERSION CONTROL")
    print("# This file is intended to be used with .env.example")
    
    # Generate JWT keys
    private_key, public_key = generate_jwt_keys()
    
    # Print secrets
    print(f"JWT_PRIVATE_KEY={private_key.replace(os.linesep, ' ')}")
    print(f"JWT_PUBLIC_KEY={public_key.replace(os.linesep, ' ')}")
    
    # Generate other secrets
    print(f"SECRET_KEY={os.urandom(32).hex()}")
    print(f"REDIS_PASSWORD={os.urandom(16).hex()}")
    print("POSTGRES_PASSWORD=change_me")
    print("CLICKHOUSE_PASSWORD=change_me")
    
    # OAuth secrets (for development only)
    print("OAUTH_YANDEX_CLIENT_ID=dev_yandex_client_id")
    print("OAUTH_YANDEX_CLIENT_SECRET=dev_yandex_client_secret")
    print("OAUTH_GOOGLE_CLIENT_ID=dev_google_client_id")
    print("OAUTH_GOOGLE_CLIENT_SECRET=dev_google_client_secret")
    print("OAUTH_VK_CLIENT_ID=dev_vk_client_id")
    print("OAUTH_VK_CLIENT_SECRET=dev_vk_client_secret")

if __name__ == "__main__":
    main()