from datetime import datetime
from enum import Enum as PyEnum
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class UserRole(str, PyEnum):
    FREE_USER = "free_user"
    PAID_USER = "paid_user"
    COMPANY_ADMIN = "company_admin"
    PLATFORM_ADMIN = "platform_admin"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(sa.String(72), nullable=False)
    full_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    company_name: Mapped[str | None] = mapped_column(sa.String(255))
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole), nullable=False, default=UserRole.FREE_USER
    )
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    totp_secret: Mapped[str | None] = mapped_column(sa.String(32))
    totp_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    failed_login_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))