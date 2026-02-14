"""User schemas for auth service."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserStatus(str, Enum):
    """User status."""
    inactive = "inactive"
    active = "active"
    verified = "verified"
    disabled = "disabled"


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str
    company_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserOut(UserBase):
    """User output schema."""
    id: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: str


class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""
    user_id: str
    email: str
    role: str


class OAuthProvider(str, Enum):
    """OAuth providers."""
    yandex = "yandex"
    google = "google"
    vk = "vk"


class OAuthLoginRequest(BaseModel):
    """OAuth login request."""
    provider: OAuthProvider
    code: str
    redirect_uri: str


class OAuthLoginResponse(BaseModel):
    """OAuth login response."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    provider: OAuthProvider
    expires_in: int


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirm."""
    token: str
    new_password: str = Field(..., min_length=8)


class VerificationEmailRequest(BaseModel):
    """Verification email request."""
    email: EmailStr