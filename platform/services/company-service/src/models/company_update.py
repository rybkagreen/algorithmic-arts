import uuid

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel, TimestampMixin


class CompanyUpdate(BaseModel, TimestampMixin):
    __tablename__ = "company_updates"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False)
    update_type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    source_url = Column(String(2048))
    published_at = Column(DateTime(timezone=True), nullable=False)