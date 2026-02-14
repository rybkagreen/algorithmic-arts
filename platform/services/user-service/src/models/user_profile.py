from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    avatar_url: Mapped[str | None] = mapped_column(sa.String(2048))
    bio: Mapped[str | None] = mapped_column(sa.Text())
    job_title: Mapped[str | None] = mapped_column(sa.String(255))
    location: Mapped[str | None] = mapped_column(sa.String(255))
    timezone: Mapped[str | None] = mapped_column(sa.String(100))
    language: Mapped[str | None] = mapped_column(sa.String(10))
    theme_preference: Mapped[str] = mapped_column(sa.String(20), default="light")
    email_notifications: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    push_notifications: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    sms_notifications: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    two_factor_method: Mapped[str | None] = mapped_column(sa.String(20))
    last_active_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))