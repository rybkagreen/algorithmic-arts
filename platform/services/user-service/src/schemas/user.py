"""User schemas for user service."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User roles."""
    free_user = "free_user"
    paid_user = "paid_user"
    company_admin = "company_admin"
    platform_admin = "platform_admin"


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str
    company_id: Optional[str] = None
    role: UserRole = UserRole.free_user


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = None
    company_id: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserOut(UserBase):
    """User output schema."""
    id: str
    created_at: str
    updated_at: str


class CompanyBase(BaseModel):
    """Base company schema."""
    name: str
    slug: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters_country: Optional[str] = None
    employees_count: Optional[int] = None


class CompanyCreate(CompanyBase):
    """Company creation schema."""
    pass


class CompanyUpdate(BaseModel):
    """Company update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters_country: Optional[str] = None
    employees_count: Optional[int] = None


class CompanyOut(CompanyBase):
    """Company output schema."""
    id: str
    created_at: str
    updated_at: str