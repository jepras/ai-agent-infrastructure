from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime, timedelta
import json

from ..models.database import User, UserCredential, UserProfile, UsageLimit
from ..core.encryption import encryption_manager


class AuthManager:
    def __init__(self, db: Session):
        self.db = db

    def _parse_user_id(self, user_id: str) -> uuid.UUID:
        """Parse user ID, handling fallback IDs from NextAuth"""
        try:
            print(f"Parsing user ID: {user_id}")
            # If it's a fallback user ID from NextAuth, extract the email and find/create user
            if user_id.startswith("user-"):
                email = user_id.replace("user-", "")
                print(f"Fallback user ID detected, email: {email}")
                user = self.get_user_by_email(email)
                if not user:
                    print(f"User not found, creating new user for email: {email}")
                    # Create the user if it doesn't exist
                    user = self.create_user(email=email, name=email.split("@")[0])
                    print(f"Created user with ID: {user.id}")
                else:
                    print(f"Found existing user with ID: {user.id}")
                return user.id
            else:
                # Assume it's a valid UUID
                print(f"Treating as UUID: {user_id}")
                return uuid.UUID(user_id)
        except (ValueError, AttributeError) as e:
            print(f"Error parsing user ID {user_id}: {e}")
            raise ValueError(f"Invalid user ID format: {user_id}")

    # User Management
    def create_user(
        self, email: str, name: Optional[str] = None, image: Optional[str] = None
    ) -> User:
        """Create a new user"""
        try:
            user = User(
                id=uuid.uuid4(),
                email=email,
                name=name,
                image=image,
                email_verified=datetime.utcnow(),
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            # Create user profile
            profile = UserProfile(id=user.id)
            self.db.add(profile)

            # Create default usage limits
            usage_limit = UsageLimit(user_id=user.id)
            self.db.add(usage_limit)

            self.db.commit()
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User with this email already exists")

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            print(f"Error getting user by email {email}: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user_uuid = self._parse_user_id(user_id)
            return self.db.query(User).filter(User.id == user_uuid).first()
        except ValueError:
            return None

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user

    # Credential Management
    def store_credential(
        self,
        user_id: str,
        credential_type: str,
        data: Any,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
    ) -> UserCredential:
        """Store encrypted credential for a user"""
        # Convert data to JSON string if it's a dict
        if isinstance(data, dict):
            data_str = json.dumps(data)
        else:
            data_str = str(data)

        # Encrypt the data
        encrypted_data = encryption_manager.encrypt(data_str)

        # Parse user_id to UUID
        user_uuid = self._parse_user_id(user_id)

        # Check if credential already exists
        existing = (
            self.db.query(UserCredential)
            .filter(
                UserCredential.user_id == user_uuid,
                UserCredential.credential_type == credential_type,
            )
            .first()
        )

        if existing:
            # Update existing credential
            existing.encrypted_data = encrypted_data
            existing.expires_at = expires_at
            existing.metadata = metadata
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new credential
            credential = UserCredential(
                user_id=user_uuid,
                credential_type=credential_type,
                encrypted_data=encrypted_data,
                expires_at=expires_at,
                metadata=metadata,
            )
            self.db.add(credential)
            self.db.commit()
            self.db.refresh(credential)
            return credential

    def get_credential(self, user_id: str, credential_type: str) -> Optional[Any]:
        """Get decrypted credential for a user"""
        try:
            user_uuid = self._parse_user_id(user_id)
            credential = (
                self.db.query(UserCredential)
                .filter(
                    UserCredential.user_id == user_uuid,
                    UserCredential.credential_type == credential_type,
                    UserCredential.is_active == True,
                )
                .first()
            )

            if not credential:
                return None

            # Check if expired
            if credential.expires_at and credential.expires_at < datetime.utcnow():
                return None

            # Decrypt and return
            decrypted_data = encryption_manager.decrypt(credential.encrypted_data)

            # Try to parse as JSON, fallback to string
            try:
                return json.loads(decrypted_data)
            except json.JSONDecodeError:
                return decrypted_data
        except (ValueError, Exception) as e:
            print(f"Error getting credential {credential_type} for user {user_id}: {e}")
            return None

    def delete_credential(self, user_id: str, credential_type: str) -> bool:
        """Delete a credential for a user"""
        try:
            user_uuid = self._parse_user_id(user_id)
            credential = (
                self.db.query(UserCredential)
                .filter(
                    UserCredential.user_id == user_uuid,
                    UserCredential.credential_type == credential_type,
                )
                .first()
            )

            if credential:
                self.db.delete(credential)
                self.db.commit()
                return True
            return False
        except ValueError:
            return False

    def get_user_credentials(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all credentials for a user (without decrypted data)"""
        try:
            print(f"Getting credentials for user_id: {user_id}")
            user_uuid = self._parse_user_id(user_id)
            print(f"Converted to UUID: {user_uuid}")
            credentials = (
                self.db.query(UserCredential)
                .filter(UserCredential.user_id == user_uuid)
                .all()
            )

            result = []
            for cred in credentials:
                result.append(
                    {
                        "id": str(cred.id),
                        "credential_type": cred.credential_type,
                        "is_active": cred.is_active,
                        "expires_at": cred.expires_at,
                        "metadata": cred.metadata,
                        "created_at": cred.created_at,
                        "updated_at": cred.updated_at,
                    }
                )

            return result
        except (ValueError, Exception) as e:
            print(f"Error getting user credentials for {user_id}: {e}")
            return []

    # OAuth Integration Methods
    def get_oauth_tokens(self, user_id: str, service: str) -> Optional[Dict[str, Any]]:
        """Get OAuth tokens for a service"""
        credential_type = f"{service}_oauth"
        return self.get_credential(user_id, credential_type)

    def store_oauth_tokens(
        self,
        user_id: str,
        service: str,
        tokens: Dict[str, Any],
        user_info: Optional[Dict[str, Any]] = None,
    ):
        """Store OAuth tokens for a service"""
        credential_type = f"{service}_oauth"

        # Calculate expiration
        expires_at = None
        if "expires_in" in tokens:
            expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])

        # Store with user info in metadata
        metadata = {"user_info": user_info} if user_info else None

        return self.store_credential(
            user_id=user_id,
            credential_type=credential_type,
            data=tokens,
            expires_at=expires_at,
            metadata=metadata,
        )

    def is_service_connected(self, user_id: str, service: str) -> bool:
        """Check if a service is connected for a user"""
        try:
            tokens = self.get_oauth_tokens(user_id, service)
            return tokens is not None
        except Exception as e:
            print(f"Error checking service connection for {service}: {e}")
            return False

    def disconnect_service(self, user_id: str, service: str) -> bool:
        """Disconnect a service for a user"""
        return self.delete_credential(user_id, f"{service}_oauth")

    # Profile Management
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        try:
            user_uuid = self._parse_user_id(user_id)
            return (
                self.db.query(UserProfile).filter(UserProfile.id == user_uuid).first()
            )
        except ValueError:
            return None

    def update_user_profile(self, user_id: str, **kwargs) -> Optional[UserProfile]:
        """Update user profile"""
        profile = self.get_user_profile(user_id)
        if not profile:
            # Create profile if it doesn't exist
            try:
                user_uuid = self._parse_user_id(user_id)
                profile = UserProfile(id=user_uuid)
                self.db.add(profile)
            except ValueError:
                return None

        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(profile)
        return profile

    # Usage Limits Management
    def get_usage_limits(self, user_id: str) -> Optional[UsageLimit]:
        """Get user usage limits"""
        try:
            user_uuid = self._parse_user_id(user_id)
            return (
                self.db.query(UsageLimit)
                .filter(UsageLimit.user_id == user_uuid)
                .first()
            )
        except ValueError:
            return None

    def update_usage_limits(self, user_id: str, **kwargs) -> Optional[UsageLimit]:
        """Update user usage limits"""
        limits = self.get_usage_limits(user_id)
        if not limits:
            # Create limits if they don't exist
            try:
                user_uuid = self._parse_user_id(user_id)
                limits = UsageLimit(user_id=user_uuid)
                self.db.add(limits)
            except ValueError:
                return None

        for key, value in kwargs.items():
            if hasattr(limits, key):
                setattr(limits, key, value)

        limits.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(limits)
        return limits

    # Service Status
    def get_service_status(self, user_id: str) -> Dict[str, bool]:
        """Get status of all connected services for a user"""
        try:
            return {
                "outlook": self.is_service_connected(user_id, "outlook"),
                "pipedrive": self.is_service_connected(user_id, "pipedrive"),
                "openai": False,
                "anthropic": False,
            }
        except Exception as e:
            # Log the error and return default status
            print(f"Error getting service status for user {user_id}: {e}")
            return {
                "outlook": False,
                "pipedrive": False,
                "openai": False,
                "anthropic": False,
            }
