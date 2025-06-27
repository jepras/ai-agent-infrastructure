"""
Pipedrive OAuth provider implementation
"""

from typing import Dict, Any
from urllib.parse import urlencode
import httpx
from sqlalchemy.orm import Session

from .base import BaseOAuthProvider


class PipedriveOAuthProvider(BaseOAuthProvider):
    """Pipedrive OAuth provider"""

    def __init__(
        self, db: Session, client_id: str, client_secret: str, redirect_uri: str
    ):
        super().__init__(db, client_id, client_secret, redirect_uri)
        self.auth_url = "https://oauth.pipedrive.com/oauth/authorize"
        self.token_url = "https://oauth.pipedrive.com/oauth/token"
        self.api_url = "https://api.pipedrive.com/v1"

    def get_authorization_url(self, user_id: str, **kwargs) -> str:
        state = self.state_manager.create_state(user_id, "pipedrive", **kwargs)
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
        }
        return f"{self.auth_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(
        self, code: str, state_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            tokens = response.json()
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token"),
                "expires_in": tokens.get("expires_in", 3600),
                "token_type": tokens.get("token_type", "Bearer"),
            }

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            tokens = response.json()
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token", refresh_token),
                "expires_in": tokens.get("expires_in", 3600),
                "token_type": tokens.get("token_type", "Bearer"),
            }

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(f"{self.api_url}/users/me", headers=headers)
            response.raise_for_status()
            user_data = response.json().get("data", {})
            return {
                "id": user_data.get("id"),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
            }
