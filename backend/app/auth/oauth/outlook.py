"""
Outlook/Microsoft Graph OAuth provider implementation
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode
import httpx
from sqlalchemy.orm import Session

from .base import BaseOAuthProvider


class OutlookOAuthProvider(BaseOAuthProvider):
    """Outlook/Microsoft Graph OAuth provider"""

    def __init__(
        self, db: Session, client_id: str, client_secret: str, redirect_uri: str
    ):
        super().__init__(db, client_id, client_secret, redirect_uri)
        self.auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        self.token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        self.graph_url = "https://graph.microsoft.com/v1.0"

    def get_authorization_url(self, user_id: str, **kwargs) -> str:
        """Get the authorization URL for Outlook OAuth flow"""
        state = self.state_manager.create_state(user_id, "outlook", **kwargs)

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "offline_access Mail.Read Mail.Send User.Read",
            "state": state,
            "response_mode": "query",
        }

        return f"{self.auth_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(
        self, code: str, state_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
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
        """Refresh access tokens using refresh token"""
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
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
        """Get user information from Microsoft Graph"""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(f"{self.graph_url}/me", headers=headers)
            response.raise_for_status()

            user_data = response.json()
            return {
                "id": user_data["id"],
                "email": user_data["mail"] or user_data["userPrincipalName"],
                "name": user_data.get("displayName"),
                "given_name": user_data.get("givenName"),
                "family_name": user_data.get("surname"),
            }

    async def get_emails(self, access_token: str, limit: int = 10) -> Dict[str, Any]:
        """Get recent emails from Outlook"""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            params = {
                "$top": limit,
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,body,from,toRecipients,receivedDateTime",
            }

            response = await client.get(
                f"{self.graph_url}/me/messages", headers=headers, params=params
            )
            response.raise_for_status()

            return response.json()

    async def send_email(
        self, access_token: str, email_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send email via Microsoft Graph"""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = await client.post(
                f"{self.graph_url}/me/sendMail",
                headers=headers,
                json={"message": email_data},
            )
            response.raise_for_status()

            return {"success": True}

    async def create_webhook_subscription(
        self, access_token: str, webhook_url: str
    ) -> Dict[str, Any]:
        """Create a webhook subscription for email notifications"""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            subscription_data = {
                "changeType": "created",
                "notificationUrl": webhook_url,
                "resource": "/me/messages",
                "expirationDateTime": "2024-12-31T23:59:59.999Z",
                "clientState": "ai-email-processor",
            }

            response = await client.post(
                f"{self.graph_url}/subscriptions",
                headers=headers,
                json=subscription_data,
            )
            response.raise_for_status()

            return response.json()
