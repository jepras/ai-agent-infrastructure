"""
Base OAuth classes for unified authentication system
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import secrets
import string
from urllib.parse import urlencode, urljoin
import httpx
from sqlalchemy.orm import Session

from ...models.database import UserCredential, OAuthState as OAuthStateModel


class OAuthState:
    """Manage OAuth state for security"""

    def __init__(self, db: Session):
        self.db = db

    def create_state(self, user_id: str, service: str, **kwargs) -> str:
        """Create a new OAuth state"""
        from ...models.database import OAuthState as OAuthStateModel
        from ...auth.manager import AuthManager

        # Validate and convert user_id if needed
        auth_manager = AuthManager(self.db)

        # If user_id is not a UUID, try to get the real user ID
        if not user_id.startswith("user-"):
            # Assume it's already a valid UUID
            real_user_id = user_id
        else:
            # Extract email from fallback user ID
            email = user_id.replace("user-", "")
            user = auth_manager.get_user_by_email(email)
            if not user:
                # Create the user if it doesn't exist
                user = auth_manager.create_user(email=email, name=email.split("@")[0])
            real_user_id = str(user.id)

        state = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
        )

        # Store state in database
        state_record = OAuthStateModel(
            state=state,
            user_id=real_user_id,
            service=service,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            state_metadata=kwargs,
        )

        self.db.add(state_record)
        self.db.commit()

        return state

    def validate_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Validate and return state data"""
        from ...models.database import OAuthState as OAuthStateModel

        # Get state from database
        state_record = (
            self.db.query(OAuthStateModel)
            .filter(
                OAuthStateModel.state == state,
                OAuthStateModel.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if not state_record:
            return None

        # Convert to dict
        state_data = {
            "user_id": str(state_record.user_id),
            "service": state_record.service,
            "created_at": state_record.created_at,
            **state_record.state_metadata,
        }

        # Delete the state record after validation
        self.db.delete(state_record)
        self.db.commit()

        return state_data


class BaseOAuthProvider(ABC):
    """Base class for OAuth providers"""

    def __init__(
        self, db: Session, client_id: str, client_secret: str, redirect_uri: str
    ):
        self.db = db
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state_manager = OAuthState(db)

    @abstractmethod
    def get_authorization_url(self, user_id: str, **kwargs) -> str:
        """Get the authorization URL for OAuth flow"""
        pass

    @abstractmethod
    async def exchange_code_for_tokens(
        self, code: str, state_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        pass

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access tokens using refresh token"""
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from the OAuth provider"""
        pass

    def store_credentials(
        self, user_id: str, credential_type: str, tokens: Dict[str, Any], **kwargs
    ):
        """Store OAuth credentials in database"""
        from ...auth.manager import AuthManager

        auth_manager = AuthManager(self.db)

        # Calculate expiration
        expires_at = None
        if "expires_in" in tokens:
            expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])

        # Store the credential
        auth_manager.store_credential(
            user_id=user_id,
            credential_type=credential_type,
            data=tokens,
            expires_at=expires_at,
            metadata=kwargs,
        )

    def get_stored_credentials(
        self, user_id: str, credential_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get stored OAuth credentials from database"""
        from ...auth.manager import AuthManager

        auth_manager = AuthManager(self.db)
        credentials = auth_manager.get_user_credentials(user_id)

        for cred in credentials:
            if cred.get("credential_type") == credential_type:
                return cred

        return None


class OAuthManager:
    """Unified OAuth manager for all providers"""

    def __init__(self, db: Session):
        self.db = db
        self.providers: Dict[str, BaseOAuthProvider] = {}

    def register_provider(self, name: str, provider: BaseOAuthProvider):
        """Register an OAuth provider"""
        self.providers[name] = provider

    def get_provider(self, name: str) -> Optional[BaseOAuthProvider]:
        """Get a registered OAuth provider"""
        return self.providers.get(name)

    def get_authorization_url(self, provider_name: str, user_id: str, **kwargs) -> str:
        """Get authorization URL for a provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"OAuth provider '{provider_name}' not found")

        return provider.get_authorization_url(user_id, **kwargs)

    async def handle_callback(
        self, provider_name: str, code: str, state: str
    ) -> Dict[str, Any]:
        """Handle OAuth callback for a provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"OAuth provider '{provider_name}' not found")

        # Validate state
        state_data = provider.state_manager.validate_state(state)
        if not state_data:
            raise ValueError("Invalid or expired OAuth state")

        # Exchange code for tokens
        tokens = await provider.exchange_code_for_tokens(code, state_data)

        # Get user info
        user_info = await provider.get_user_info(tokens["access_token"])

        # Store credentials
        credential_type = f"{provider_name}_oauth"
        provider.store_credentials(
            user_id=state_data["user_id"],
            credential_type=credential_type,
            tokens=tokens,
            user_info=user_info,
        )

        return {
            "user_id": state_data["user_id"],
            "tokens": tokens,
            "user_info": user_info,
        }
