#!/usr/bin/env python3
"""
Generate a proper Fernet encryption key for the application
"""

from cryptography.fernet import Fernet
import base64
import os


def generate_encryption_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    return key.decode("utf-8")


def main():
    print("🔐 Generating Fernet encryption key...")

    # Generate the key
    key = generate_encryption_key()

    print(f"\n✅ Generated encryption key:")
    print(f"CREDENTIAL_ENCRYPTION_KEY={key}")

    print(f"\n📝 Add this to your .env file:")
    print(f"CREDENTIAL_ENCRYPTION_KEY={key}")

    # Also generate a NextAuth secret
    nextauth_secret = base64.b64encode(os.urandom(32)).decode("utf-8")
    print(f"\n🔑 NextAuth secret:")
    print(f"NEXTAUTH_SECRET={nextauth_secret}")

    print(f"\n📝 Add this to your .env file as well:")
    print(f"NEXTAUTH_SECRET={nextauth_secret}")


if __name__ == "__main__":
    main()
