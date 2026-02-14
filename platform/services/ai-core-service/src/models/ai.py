"""AI models for AI core service."""

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
    Float,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin

class AIAnalysis(BaseModel, TimestampMixin):
    __tablename__ = "ai_analyses"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id_1 = Column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    company_id_2 = Column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    compatibility_score = Column(Float, nullable=False)
    factors = Column(Text)  # JSON string
    explanation = Column(Text)
    analysis_style = Column(Enum("formal", "friendly", "technical"), nullable=False, default="technical")
    language = Column(Enum("russian", "english"), nullable=False, default="russian")
    
    # Relationships
    company_1 = relationship("Company", foreign_keys=[company_id_1])
    company_2 = relationship("Company", foreign_keys=[company_id_2])


class OutreachMessage(BaseModel, TimestampMixin):
    __tablename__ = "outreach_messages"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(PGUUID(as_uuid=True), ForeignKey("ai_analyses.id", ondelete="CASCADE"), nullable=False)
    recipient_name = Column(String(255), nullable=False)
    recipient_email = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    style = Column(Enum("formal", "friendly", "technical"), nullable=False, default="formal")
    language = Column(Enum("russian", "english"), nullable=False, default="russian")
    sent_at = Column(DateTime(timezone=True))
    status = Column(Enum("draft", "sent", "failed"), nullable=False, default="draft")
    
    # Relationships
    analysis = relationship("AIAnalysis")


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