"""OAuth service for auth service."""

import json
import httpx
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

from shared.logging import get_logger
from .config import settings
from .repositories.user_repository import UserRepository
from .core.exceptions import UserNotFoundError, InvalidCredentialsError
from .schemas.user import OAuthProvider, OAuthLoginRequest, OAuthLoginResponse, UserOut

logger = get_logger("oauth-service")


class OAuthService:
    """OAuth service for social login."""
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.http_client = httpx.AsyncClient(timeout=10.0)
    
    async def get_oauth_provider_config(self, provider: OAuthProvider) -> Dict[str, str]:
        """Get OAuth provider configuration."""
        configs = {
            "yandex": {
                "authorize_url": "https://oauth.yandex.ru/authorize",
                "token_url": "https://oauth.yandex.ru/token",
                "userinfo_url": "https://login.yandex.ru/info",
                "client_id": settings.oauth.yandex.client_id,
                "client_secret": settings.oauth.yandex.client_secret,
                "scope": "login:email login:info"
            },
            "google": {
                "authorize_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
                "client_id": settings.oauth.google.client_id,
                "client_secret": settings.oauth.google.client_secret,
                "scope": "openid email profile"
            },
            "vk": {
                "authorize_url": "https://oauth.vk.com/authorize",
                "token_url": "https://oauth.vk.com/access_token",
                "userinfo_url": "https://api.vk.com/method/users.get",
                "client_id": settings.oauth.vk.client_id,
                "client_secret": settings.oauth.vk.client_secret,
                "scope": "email"
            }
        }
        
        if provider not in configs:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
        
        return configs[provider]
    
    async def exchange_code_for_token(
        self, provider: OAuthProvider, code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        config = await self.get_oauth_provider_config(provider)
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"]
        }
        
        try:
            response = await self.http_client.post(
                config["token_url"],
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to exchange code for token", 
                        provider=provider, error=str(e))
            raise InvalidCredentialsError(f"Failed to authenticate with {provider}")
    
    async def get_user_info(
        self, provider: OAuthProvider, access_token: str
    ) -> Dict[str, Any]:
        """Get user info from OAuth provider."""
        config = await self.get_oauth_provider_config(provider)
        
        try:
            if provider == "yandex":
                response = await self.http_client.get(
                    config["userinfo_url"],
                    headers={"Authorization": f"OAuth {access_token}"}
                )
            elif provider == "google":
                response = await self.http_client.get(
                    config["userinfo_url"],
                    headers={"Authorization": f"Bearer {access_token}"}
                )
            elif provider == "vk":
                response = await self.http_client.get(
                    config["userinfo_url"],
                    params={
                        "access_token": access_token,
                        "fields": "id,first_name,last_name,email",
                        "v": "5.131"
                    }
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Normalize user info across providers
            if provider == "yandex":
                return {
                    "id": data.get("id"),
                    "email": data.get("default_email"),
                    "full_name": f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
                    "provider": provider
                }
            elif provider == "google":
                return {
                    "id": data.get("sub"),
                    "email": data.get("email"),
                    "full_name": f"{data.get('given_name', '')} {data.get('family_name', '')}".strip(),
                    "provider": provider
                }
            elif provider == "vk":
                user_data = data.get("response", [{}])[0]
                return {
                    "id": str(user_data.get("id")),
                    "email": user_data.get("email"),
                    "full_name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
                    "provider": provider
                }
                
        except Exception as e:
            logger.error("Failed to get user info", provider=provider, error=str(e))
            raise InvalidCredentialsError(f"Failed to get user info from {provider}")
    
    async def create_or_get_user_from_oauth(
        self, provider: OAuthProvider, external_id: str, email: str, full_name: str
    ) -> UserOut:
        """Create or get existing user from OAuth connection."""
        async with get_db() as db:
            # Check if user exists by email
            existing_user = await self.user_repository.get_by_email(db, email)
            if existing_user:
                # Check if OAuth connection exists
                oauth_conn = await self.user_repository.get_oauth_connection(
                    db, provider.value, external_id
                )
                if not oauth_conn:
                    # Create OAuth connection for existing user
                    await self.user_repository.create_oauth_connection(
                        db, existing_user.id, provider.value, external_id,
                        access_token="", refresh_token="", expires_at=None
                    )
                return UserOut(**self.user_repository.to_dict(existing_user))
            
            # Create new user
            user_data = {
                "email": email,
                "full_name": full_name,
                "role": "free_user",
                "is_active": True,
                "is_verified": True
            }
            
            user = await self.user_repository.create_user(db, user_data)
            
            # Create OAuth connection
            await self.user_repository.create_oauth_connection(
                db, user.id, provider.value, external_id,
                access_token="", refresh_token="", expires_at=None
            )
            
            return UserOut(**self.user_repository.to_dict(user))
    
    async def login_with_oauth(
        self, provider: OAuthProvider, code: str, redirect_uri: str
    ) -> OAuthLoginResponse:
        """Complete OAuth login flow."""
        # Exchange code for token
        token_data = await self.exchange_code_for_token(provider, code, redirect_uri)
        
        # Get user info
        user_info = await self.get_user_info(provider, token_data.get("access_token"))
        
        # Create or get user
        user = await self.create_or_get_user_from_oauth(
            provider,
            user_info["id"],
            user_info["email"],
            user_info["full_name"]
        )
        
        # Generate JWT tokens
        from .services.jwt_service import JWTService
        jwt_service = JWTService()
        
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }
        
        access_token = jwt_service.encode_access_token(token_data)
        refresh_token = jwt_service.encode_refresh_token(token_data)
        
        # Store refresh token
        expires_at = datetime.utcnow() + timedelta(days=settings.jwt.refresh_token_expire_days)
        async with get_db() as db:
            await self.user_repository.create_refresh_token(
                db, user.id, refresh_token, expires_at
            )
        
        return OAuthLoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user,
            provider=provider,
            expires_in=settings.jwt.access_token_expire_minutes * 60
        )