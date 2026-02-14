"""Partner model for partner service."""

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


class Partnership(BaseModel, TimestampMixin):
    __tablename__ = "partnerships"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id_1 = Column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    company_id_2 = Column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("proposed", "accepted", "rejected", "active", "terminated"), nullable=False, default="proposed")
    compatibility_score = Column(Float, default=0.0)
    reason = Column(Text)
    created_by_user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    updated_by_user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    company_1 = relationship("Company", foreign_keys=[company_id_1])
    company_2 = relationship("Company", foreign_keys=[company_id_2])
    
    __table_args__ = (
        UniqueConstraint("company_id_1", "company_id_2", name="uq_partnerships_company_1_company_2"),
        UniqueConstraint("company_id_2", "company_id_1", name="uq_partnerships_company_2_company_1"),
    )


class PartnershipMetric(BaseModel, TimestampMixin):
    __tablename__ = "partnership_metrics"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partnership_id = Column(PGUUID(as_uuid=True), ForeignKey("partnerships.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    partnership = relationship("Partnership")


class PartnershipUpdate(BaseModel, TimestampMixin):
    __tablename__ = "partnership_updates"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partnership_id = Column(PGUUID(as_uuid=True), ForeignKey("partnerships.id", ondelete="CASCADE"), nullable=False)
    update_type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    source_url = Column(String(2048))
    published_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    partnership = relationship("Partnership")