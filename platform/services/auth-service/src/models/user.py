"""User model for auth service."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    DateTime,
    Text,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin
from ..schemas import UserStatus


class User(BaseModel, TimestampMixin):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(72), nullable=False)  # bcrypt, cost 12
    full_name = Column(String(255), nullable=False)
    company_name = Column(String(255))
    role = Column(Enum("free_user", "paid_user", "company_admin", "platform_admin"), nullable=False, default="free_user")
    is_active = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    totp_secret = Column(String(32))  # NULL = 2FA отключена
    totp_enabled = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime(timezone=True))
    failed_login_count = Column(Integer, nullable=False, default=0)

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    oauth_connections = relationship("OAuthConnection", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("email", "deleted_at", name="uq_users_email_deleted_at"),
    )


class RefreshToken(BaseModel, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(64), nullable=False, unique=True)  # SHA-256 от токена
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        UniqueConstraint("token_hash", "revoked_at", name="uq_refresh_tokens_token_hash_revoked_at"),
    )


class OAuthConnection(BaseModel, TimestampMixin):
    __tablename__ = "oauth_connections"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(Enum("yandex", "google", "vk"), nullable=False)
    external_id = Column(String(255), nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="oauth_connections")

    __table_args__ = (
        UniqueConstraint("provider", "external_id", name="uq_oauth_connections_provider_external_id"),
    )


class VerificationToken(BaseModel, TimestampMixin):
    __tablename__ = "verification_tokens"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(64), nullable=False, unique=True)  # SHA-256 от токена
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    type = Column(Enum("email_verification", "password_reset"), nullable=False)

    # Relationships
    user = relationship("User")