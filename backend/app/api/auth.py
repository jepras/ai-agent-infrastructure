from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import secrets
import string
import os

from ..core.database import get_db
from ..auth.manager import AuthManager
from ..auth.oauth.base import OAuthManager
from ..auth.oauth.outlook import OutlookOAuthProvider
from ..auth.oauth.pipedrive import PipedriveOAuthProvider
from ..models.schemas import (
    UserCreate,
    UserResponse,
    UserProfileUpdate,
    UserProfileResponse,
    CredentialCreate,
    CredentialResponse,
    ApiKeyCreate,
    BaseResponse,
    ServiceStatusResponse,
    UsageLimitUpdate,
    UsageLimitResponse,
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


def get_auth_manager(db: Session = Depends(get_db)) -> AuthManager:
    return AuthManager(db)


def get_oauth_manager(db: Session = Depends(get_db)) -> OAuthManager:
    """Get OAuth manager with registered providers"""
    oauth_manager = OAuthManager(db)

    # Register Outlook provider
    outlook_provider = OutlookOAuthProvider(
        db=db,
        client_id=os.getenv("OUTLOOK_CLIENT_ID", ""),
        client_secret=os.getenv("OUTLOOK_CLIENT_SECRET", ""),
        redirect_uri=f"{os.getenv('NEXTAUTH_URL', 'http://localhost:3000')}/api/auth/callback/outlook",
    )
    oauth_manager.register_provider("outlook", outlook_provider)

    # Register Pipedrive provider
    pipedrive_provider = PipedriveOAuthProvider(
        db=db,
        client_id=os.getenv("PIPEDRIVE_CLIENT_ID", ""),
        client_secret=os.getenv("PIPEDRIVE_CLIENT_SECRET", ""),
        redirect_uri=f"{os.getenv('NEXTAUTH_URL', 'http://localhost:3000')}/api/auth/callback/pipedrive",
    )
    oauth_manager.register_provider("pipedrive", pipedrive_provider)

    return oauth_manager


def generate_state() -> str:
    """Generate a random state for OAuth flows"""
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
    )


# User management endpoints
@router.post("/users", response_model=UserResponse)
def create_user(
    user_data: UserCreate, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Create a new user"""
    try:
        user = auth_manager.create_user(
            email=user_data.email, name=user_data.name, image=user_data.image
        )
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, auth_manager: AuthManager = Depends(get_auth_manager)):
    """Get user by ID"""
    user = auth_manager.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse.from_orm(user)


@router.get("/users/email/{email}", response_model=UserResponse)
def get_user_by_email(
    email: str, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Get user by email"""
    user = auth_manager.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse.from_orm(user)


# OAuth endpoints
@router.post("/oauth/connect")
async def connect_oauth(
    request: Request, oauth_manager: OAuthManager = Depends(get_oauth_manager)
):
    """Initiate OAuth flow for a service"""
    try:
        body = await request.json()
        service = body.get("provider")
        user_id = body.get("user_id")

        if not service or not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing provider or user_id",
            )

        auth_url = oauth_manager.get_authorization_url(service, user_id)
        return {"oauth_url": auth_url}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/connect/{service}")
def initiate_oauth(
    service: str, user_id: str, oauth_manager: OAuthManager = Depends(get_oauth_manager)
):
    """Initiate OAuth flow for a service"""
    try:
        auth_url = oauth_manager.get_authorization_url(service, user_id)
        return {"auth_url": auth_url}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/callback/{service}")
async def oauth_callback(
    service: str,
    code: str,
    state: str,
    oauth_manager: OAuthManager = Depends(get_oauth_manager),
):
    """Handle OAuth callback for a service"""
    try:
        result = await oauth_manager.handle_callback(service, code, state)
        return {
            "success": True,
            "user_id": result["user_id"],
            "service": service,
            "user_info": result.get("user_info"),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/disconnect/{service}")
def disconnect_service(
    service: str, user_id: str, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Disconnect a service for a user"""
    success = auth_manager.disconnect_service(user_id, service)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not connected"
        )
    return BaseResponse(message=f"{service} disconnected successfully")


# Profile management endpoints
@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
def get_user_profile(
    user_id: str, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Get user profile"""
    profile = auth_manager.get_user_profile(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
        )
    return UserProfileResponse.from_orm(profile)


@router.put("/users/{user_id}/profile", response_model=UserProfileResponse)
def update_user_profile(
    user_id: str,
    profile_data: UserProfileUpdate,
    auth_manager: AuthManager = Depends(get_auth_manager),
):
    """Update user profile"""
    profile = auth_manager.update_user_profile(
        user_id, **profile_data.dict(exclude_unset=True)
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserProfileResponse.from_orm(profile)


# Credential management endpoints
@router.post("/users/{user_id}/credentials", response_model=CredentialResponse)
def store_credential(
    user_id: str,
    credential_data: CredentialCreate,
    auth_manager: AuthManager = Depends(get_auth_manager),
):
    """Store a credential for a user"""
    credential = auth_manager.store_credential(
        user_id=user_id,
        credential_type=credential_data.credential_type,
        data=credential_data.data,
        expires_at=credential_data.expires_at,
        metadata=credential_data.metadata,
    )
    return CredentialResponse.from_orm(credential)


@router.get("/users/{user_id}/credentials", response_model=List[CredentialResponse])
def get_user_credentials(
    user_id: str, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Get all credentials for a user (without decrypted data)"""
    credentials = auth_manager.get_user_credentials(user_id)
    return [CredentialResponse(**cred) for cred in credentials]


@router.delete(
    "/users/{user_id}/credentials/{credential_type}", response_model=BaseResponse
)
def delete_credential(
    user_id: str,
    credential_type: str,
    auth_manager: AuthManager = Depends(get_auth_manager),
):
    """Delete a credential for a user"""
    success = auth_manager.delete_credential(user_id, credential_type)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found"
        )
    return BaseResponse(message="Credential deleted successfully")


# API key management endpoints
@router.post("/users/{user_id}/api-keys", response_model=CredentialResponse)
def store_api_key(
    user_id: str,
    api_key_data: ApiKeyCreate,
    auth_manager: AuthManager = Depends(get_auth_manager),
):
    """Store an API key for a user"""
    credential_type = f"{api_key_data.provider}_api_key"
    credential = auth_manager.store_credential(
        user_id=user_id, credential_type=credential_type, data=api_key_data.api_key
    )
    return CredentialResponse.from_orm(credential)


# Service status endpoint
@router.get("/users/{user_id}/service-status", response_model=ServiceStatusResponse)
def get_service_status(
    user_id: str, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Get status of all connected services for a user"""
    return auth_manager.get_service_status(user_id)


# Usage limits endpoints
@router.get("/users/{user_id}/usage-limits", response_model=UsageLimitResponse)
def get_usage_limits(
    user_id: str, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Get user usage limits"""
    limits = auth_manager.get_usage_limits(user_id)
    if not limits:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usage limits not found"
        )
    return UsageLimitResponse.from_orm(limits)


@router.put("/users/{user_id}/usage-limits", response_model=UsageLimitResponse)
def update_usage_limits(
    user_id: str,
    limits_data: UsageLimitUpdate,
    auth_manager: AuthManager = Depends(get_auth_manager),
):
    """Update user usage limits"""
    limits = auth_manager.update_usage_limits(
        user_id, **limits_data.dict(exclude_unset=True)
    )
    if not limits:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UsageLimitResponse.from_orm(limits)


# Simple authentication endpoint (for testing)
@router.post("/simple-auth")
def simple_auth(email: str):
    """Simple authentication for testing purposes"""
    return {"email": email, "authenticated": True}
