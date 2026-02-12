"""Auth service for auth service."""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import bcrypt
import secrets

from shared.logging import get_logger
from .config import settings
from .jwt_service import JWTService
from .repositories.user_repository import UserRepository
from .core.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserAlreadyExistsError,
    EmailVerificationRequiredError,
)
from .schemas.user import UserCreate, UserOut, Token, TokenData

logger = get_logger("auth-service")


class AuthService:
    """Auth service."""
    
    def __init__(self):
        self.jwt_service = JWTService()
        self.user_repository = UserRepository()
    
    async def register(self, user_data: UserCreate) -> UserOut:
        """Register new user."""
        # Check if user exists
        async with get_db() as db:
            existing_user = await self.user_repository.get_by_email(db, user_data.email)
            if existing_user:
                raise UserAlreadyExistsError()
        
        # Hash password
        hashed_password = bcrypt.hashpw(
            user_data.password.encode('utf-8'), 
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')
        
        # Create user
        user_data_dict = user_data.model_dump()
        user_data_dict['password_hash'] = hashed_password
        
        async with get_db() as db:
            user = await self.user_repository.create_user(db, user_data_dict)
            
            # Return user data
            return UserOut(**self.user_repository.to_dict(user))
    
    async def authenticate(self, login_data: dict) -> Token:
        """Authenticate user and return tokens."""
        email = login_data.get('email')
        password = login_data.get('password')
        
        if not email or not password:
            raise InvalidCredentialsError()
        
        async with get_db() as db:
            user = await self.user_repository.get_by_email(db, email)
            if not user:
                raise InvalidCredentialsError()
            
            # Check password
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                # Increment failed login count
                await db.execute(
                    update(User)
                    .where(User.id == user.id)
                    .values(failed_login_count=User.failed_login_count + 1)
                )
                await db.commit()
                raise InvalidCredentialsError()
            
            # Reset failed login count
            await db.execute(
                update(User)
                .where(User.id == user.id)
                .values(failed_login_count=0)
            )
            await db.commit()
            
            # Check if user is active and verified
            if not user.is_active:
                raise InvalidCredentialsError("User is not active")
            if not user.is_verified:
                raise EmailVerificationRequiredError()
            
            # Generate tokens
            token_data = {
                "user_id": str(user.id),
                "email": user.email,
                "role": user.role.value
            }
            
            access_token = self.jwt_service.encode_access_token(token_data)
            refresh_token = self.jwt_service.encode_refresh_token(token_data)
            
            # Store refresh token
            expires_at = datetime.utcnow() + timedelta(days=settings.jwt.refresh_token_expire_days)
            await self.user_repository.create_refresh_token(
                db, user.id, refresh_token, expires_at
            )
            
            return Token(access_token=access_token, token_type="bearer")
    
    async def refresh_tokens(self, refresh_token: str) -> Token:
        """Refresh tokens using refresh token."""
        try:
            payload = self.jwt_service.decode_token(refresh_token)
        except Exception:
            raise InvalidCredentialsError("Invalid refresh token")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise InvalidCredentialsError("Invalid token")
        
        async with get_db() as db:
            # Check if refresh token exists and is not revoked
            token = await self.user_repository.get_refresh_token_by_hash(db, refresh_token)
            if not token:
                raise InvalidCredentialsError("Refresh token not found or revoked")
            
            # Get user
            user = await self.user_repository.get_by_id(db, user_id)
            if not user:
                raise UserNotFoundError()
            
            # Generate new tokens
            token_data = {
                "user_id": str(user.id),
                "email": user.email,
                "role": user.role.value
            }
            
            access_token = self.jwt_service.encode_access_token(token_data)
            new_refresh_token = self.jwt_service.encode_refresh_token(token_data)
            
            # Revoke old refresh token and store new one
            await self.user_repository.revoke_refresh_token(db, refresh_token)
            expires_at = datetime.utcnow() + timedelta(days=settings.jwt.refresh_token_expire_days)
            await self.user_repository.create_refresh_token(
                db, user.id, new_refresh_token, expires_at
            )
            
            return Token(access_token=access_token, token_type="bearer")