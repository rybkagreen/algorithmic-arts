from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    slug: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text())
    website: Mapped[str | None] = mapped_column(sa.String(2048))
    industry: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    sub_industries: Mapped[list[str]] = mapped_column(sa.JSON, default=list)
    business_model: Mapped[str | None] = mapped_column(sa.String(255))
    founded_year: Mapped[int | None] = mapped_column(sa.Integer)
    headquarters_country: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    headquarters_city: Mapped[str | None] = mapped_column(sa.String(255))
    employees_count: Mapped[int | None] = mapped_column(sa.Integer)
    employees_range: Mapped[str | None] = mapped_column(sa.String(50))
    funding_total_amount: Mapped[float | None] = mapped_column(sa.Float)
    funding_total_currency: Mapped[str | None] = mapped_column(sa.String(10))
    funding_stage: Mapped[str | None] = mapped_column(sa.String(50))
    last_funding_date: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    inn_value: Mapped[str | None] = mapped_column(sa.String(12))
    ogrn_value: Mapped[str | None] = mapped_column(sa.String(13))
    legal_name: Mapped[str | None] = mapped_column(sa.String(255))
    tech_stack: Mapped[dict[str, str]] = mapped_column(sa.JSON, default=dict)
    integrations: Mapped[list[str]] = mapped_column(sa.JSON, default=list)
    api_available: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    ai_summary: Mapped[str | None] = mapped_column(sa.Text())
    ai_tags: Mapped[list[str]] = mapped_column(sa.JSON, default=list)
    embedding: Mapped[list[float]] = mapped_column(sa.ARRAY(sa.Float), default=list)
    is_verified: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    view_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))


class CompanyUpdate(Base):
    """Partitioned table for company updates (range partitioning by created_at)."""
    __tablename__ = "company_updates"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    company_id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), nullable=False, index=True)
    update_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    old_value: Mapped[dict] = mapped_column(sa.JSONB, default=dict)
    new_value: Mapped[dict] = mapped_column(sa.JSONB, default=dict)
    changed_fields: Mapped[list[str]] = mapped_column(sa.ARRAY(sa.String(100)), default=list)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )


class CompanyMetric(Base):
    """Partitioned table for company metrics (hash partitioning by company_id)."""
    __tablename__ = "company_metrics"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    company_id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    value: Mapped[float] = mapped_column(sa.Numeric(precision=12, scale=4), nullable=False)
    unit: Mapped[str | None] = mapped_column(sa.String(20))
    period_start: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    period_end: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )