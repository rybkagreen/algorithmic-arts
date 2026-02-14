"""User repository for auth service."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models.user import User, RefreshToken, OAuthConnection


class UserRepository:
    """User repository."""
    
    def __init__(self):
        pass
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email (active only)."""
        stmt = select(User).where(
            User.email == email,
            User.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get user by ID (active only)."""
        stmt = select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_user(self, db: AsyncSession, user_data: dict) -> User:
        """Create new user."""
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def update_user(self, db: AsyncSession, user_id: UUID, update_data: dict) -> User:
        """Update user."""
        stmt = (
            update(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
            .values(**update_data)
            .returning(User)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    
    async def soft_delete_user(self, db: AsyncSession, user_id: UUID) -> None:
        """Soft delete user."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(deleted_at=datetime.utcnow())
        )
        await db.execute(stmt)
        await db.commit()
    
    async def create_refresh_token(
        self, db: AsyncSession, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> RefreshToken:
        """Create refresh token."""
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token
    
    async def get_refresh_token_by_hash(
        self, db: AsyncSession, token_hash: str
    ) -> Optional[RefreshToken]:
        """Get refresh token by hash (not revoked)."""
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def revoke_refresh_token(
        self, db: AsyncSession, token_hash: str
    ) -> None:
        """Revoke refresh token."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(revoked_at=datetime.utcnow())
        )
        await db.execute(stmt)
        await db.commit()
    
    async def create_oauth_connection(
        self, db: AsyncSession, user_id: UUID, provider: str, external_id: str, **kwargs
    ) -> OAuthConnection:
        """Create OAuth connection."""
        connection = OAuthConnection(
            user_id=user_id,
            provider=provider,
            external_id=external_id,
            **kwargs
        )
        db.add(connection)
        await db.commit()
        await db.refresh(connection)
        return connection
    
    async def get_oauth_connection(
        self, db: AsyncSession, provider: str, external_id: str
    ) -> Optional[OAuthConnection]:
        """Get OAuth connection."""
        stmt = select(OAuthConnection).where(
            OAuthConnection.provider == provider,
            OAuthConnection.external_id == external_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def to_dict(self, user: User) -> dict:
        """Convert user to dict."""
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }