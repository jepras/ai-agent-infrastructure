#!/usr/bin/env python3
"""
Generate required secrets for Railway deployment
"""

import secrets
import string
import base64
from cryptography.fernet import Fernet


def generate_secret(length=32):
    """Generate a random secret string"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_encryption_key():
    """Generate a Fernet encryption key"""
    return Fernet.generate_key().decode()


def main():
    print("🔐 Generating Railway Environment Variables")
    print("=" * 50)

    # Generate secrets
    nextauth_secret = generate_secret(32)
    jwt_secret = generate_secret(32)
    encryption_key = generate_encryption_key()

    print("\n📋 BACKEND SERVICE VARIABLES")
    print("Service: adaptable-liberation-production.up.railway.app")
    print("-" * 40)
    print(
        f"DATABASE_URL=postgresql://postgres:VowhsxskHrhOkMmDzCverwyLrFYBXDkD@postgres.railway.internal:5432/railway"
    )
    print(f"NEXTAUTH_URL=https://endearing-heart-production.up.railway.app")
    print(f"NEXTAUTH_SECRET={nextauth_secret}")
    print(f"CREDENTIAL_ENCRYPTION_KEY={encryption_key}")
    print(f"JWT_SECRET={jwt_secret}")
    print(f"BASE_URL=https://endearing-heart-production.up.railway.app")
    print(f"ENVIRONMENT=production")
    print(f"PORT=8000")

    print("\n📋 FRONTEND SERVICE VARIABLES")
    print("Service: endearing-heart-production.up.railway.app")
    print("-" * 40)
    print(f"NEXT_PUBLIC_API_URL=https://adaptable-liberation-production.up.railway.app")
    print(f"NEXTAUTH_URL=https://endearing-heart-production.up.railway.app")
    print(f"NEXTAUTH_SECRET={nextauth_secret}")

    print("\n⚠️  IMPORTANT NOTES:")
    print("1. Use the SAME NEXTAUTH_SECRET for both frontend and backend")
    print("2. Keep these secrets secure and don't share them")
    print("3. After setting these variables, redeploy both services")
    print("4. The OAuth variables (OUTLOOK_CLIENT_ID, etc.) are optional for now")


if __name__ == "__main__":
    main()
