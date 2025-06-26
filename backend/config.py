from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str

    # NextAuth.js
    nextauth_url: str = "http://localhost:3000"
    nextauth_secret: str

    # OAuth Applications
    outlook_client_id: str
    outlook_client_secret: str
    pipedrive_client_id: str
    pipedrive_client_secret: str

    # System Security
    credential_encryption_key: str
    jwt_secret: str

    # Application Configuration
    base_url: str = "http://localhost:3000"
    environment: str = "development"

    # AI Providers (optional, users provide their own)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Railway Configuration
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()


# Validate required settings
def validate_settings():
    """Validate that all required settings are present"""
    required_fields = [
        "database_url",
        "nextauth_secret",
        "outlook_client_id",
        "outlook_client_secret",
        "pipedrive_client_id",
        "pipedrive_client_secret",
        "credential_encryption_key",
        "jwt_secret",
    ]

    missing_fields = []
    for field in required_fields:
        if not getattr(settings, field, None):
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_fields)}"
        )


# Validate on import
if os.getenv("ENVIRONMENT") != "test":
    validate_settings()
