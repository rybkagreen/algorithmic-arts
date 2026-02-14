"""User model for user service."""

import uuid

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


class User(BaseModel, TimestampMixin):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"))
    role = Column(Enum("free_user", "paid_user", "company_admin", "platform_admin"), nullable=False, default="free_user")
    is_active = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    totp_secret = Column(String(32))  # NULL = 2FA отключена
    totp_enabled = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime(timezone=True))
    failed_login_count = Column(Integer, nullable=False, default=0)

    # Relationships
    company = relationship("Company", back_populates="users")

    __table_args__ = (
        UniqueConstraint("email", "deleted_at", name="uq_users_email_deleted_at"),
    )


class Company(BaseModel, TimestampMixin):
    __tablename__ = "companies"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    website = Column(String(1024))
    logo_url = Column(String(2048))
    industry = Column(String(100))
    sub_industries = Column(String(1000))  # JSON array stored as string
    business_model = Column(Text)
    founded_year = Column(Integer)
    headquarters_country = Column(String(100))
    headquarters_city = Column(String(100))
    employees_count = Column(Integer)
    employees_range = Column(String(50))
    funding_total = Column(String(20))  # Decimal stored as string
    funding_stage = Column(String(50))
    last_funding_date = Column(DateTime(timezone=True))
    inn = Column(String(12))
    ogrn = Column(String(13))
    kpp = Column(String(9))
    legal_name = Column(String(255))
    tech_stack = Column(String(2000))  # JSON stored as string
    integrations = Column(String(1000))  # JSON array stored as string
    api_available = Column(Boolean, default=False)
    ai_summary = Column(Text)
    ai_tags = Column(String(1000))  # JSON array stored as string
    embedding = Column(String(2000))  # Vector stored as string
    is_verified = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)

    # Relationships
    users = relationship("User", back_populates="company")

    __table_args__ = (
        UniqueConstraint("slug", "deleted_at", name="uq_companies_slug_deleted_at"),
    )