import uuid
from datetime import datetime

from sqlalchemy import ARRAY, UUID, Column, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel, TimestampMixin
from .outreach_message import OutreachMessage


class Partnership(BaseModel, TimestampMixin):
    __tablename__ = "partnerships"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_a_id = Column(PGUUID(as_uuid=True), nullable=False)
    company_b_id = Column(PGUUID(as_uuid=True), nullable=False)
    compatibility_score = Column(Numeric(3, 2))
    match_reasons = Column(ARRAY(String(255)))
    synergy_areas = Column(ARRAY(String(255)))
    analysis_method = Column(String(100))
    analyzed_by_agent = Column(String(100))
    ai_explanation = Column(Text)
    status = Column(String(50), nullable=False)
    contacted_at = Column(DateTime(timezone=True))
    partnership_started_at = Column(DateTime(timezone=True))
    deal_value = Column(Numeric(15, 2))
    revenue_generated = Column(Numeric(15, 2))