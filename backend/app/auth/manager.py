from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime, timedelta

from ..models.database import User, UserCredential, UserProfile, UsageLimit
from ..core.encryption import encryption_manager


class AuthManager:
    def __init__(self, db: Session):
        self.db = db

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
        return self.db.query(User).filter(User.id == user_id).first()

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
        data: str,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict] = None,
    ) -> UserCredential:
        """Store encrypted credential for a user"""
        # Encrypt the data
        encrypted_data = encryption_manager.encrypt(data)

        # Check if credential already exists
        existing = (
            self.db.query(UserCredential)
            .filter(
                UserCredential.user_id == user_id,
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
                user_id=user_id,
                credential_type=credential_type,
                encrypted_data=encrypted_data,
                expires_at=expires_at,
                metadata=metadata,
            )
            self.db.add(credential)
            self.db.commit()
            self.db.refresh(credential)
            return credential

    def get_credential(self, user_id: str, credential_type: str) -> Optional[str]:
        """Get decrypted credential for a user"""
        credential = (
            self.db.query(UserCredential)
            .filter(
                UserCredential.user_id == user_id,
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
        return encryption_manager.decrypt(credential.encrypted_data)

    def delete_credential(self, user_id: str, credential_type: str) -> bool:
        """Delete a credential for a user"""
        credential = (
            self.db.query(UserCredential)
            .filter(
                UserCredential.user_id == user_id,
                UserCredential.credential_type == credential_type,
            )
            .first()
        )

        if credential:
            self.db.delete(credential)
            self.db.commit()
            return True
        return False

    def get_user_credentials(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all credentials for a user (without decrypted data)"""
        credentials = (
            self.db.query(UserCredential)
            .filter(UserCredential.user_id == user_id)
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

    # Profile Management
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        return self.db.query(UserProfile).filter(UserProfile.id == user_id).first()

    def update_user_profile(self, user_id: str, **kwargs) -> Optional[UserProfile]:
        """Update user profile"""
        profile = self.get_user_profile(user_id)
        if not profile:
            # Create profile if it doesn't exist
            profile = UserProfile(id=user_id)
            self.db.add(profile)

        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(profile)
        return profile

    # Usage Limits
    def get_usage_limits(self, user_id: str) -> Optional[UsageLimit]:
        """Get user usage limits"""
        return self.db.query(UsageLimit).filter(UsageLimit.user_id == user_id).first()

    def update_usage_limits(self, user_id: str, **kwargs) -> Optional[UsageLimit]:
        """Update user usage limits"""
        limits = self.get_usage_limits(user_id)
        if not limits:
            # Create limits if they don't exist
            limits = UsageLimit(user_id=user_id)
            self.db.add(limits)

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
        credentials = self.get_user_credentials(user_id)

        status = {
            "outlook": False,
            "pipedrive": False,
            "openai": False,
            "anthropic": False,
        }

        for cred in credentials:
            if cred["credential_type"] == "outlook_oauth" and cred["is_active"]:
                status["outlook"] = True
            elif cred["credential_type"] == "pipedrive_oauth" and cred["is_active"]:
                status["pipedrive"] = True
            elif cred["credential_type"] == "openai_api_key" and cred["is_active"]:
                status["openai"] = True
            elif cred["credential_type"] == "anthropic_api_key" and cred["is_active"]:
                status["anthropic"] = True

        return status
