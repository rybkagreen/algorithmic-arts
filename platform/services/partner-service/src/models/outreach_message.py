import uuid

from sqlalchemy import Boolean, Column, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel, TimestampMixin


class OutreachMessage(BaseModel, TimestampMixin):
    __tablename__ = "outreach_messages"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partnership_id = Column(PGUUID(as_uuid=True), nullable=False)
    message_text = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=False)
    response_received = Column(Boolean, default=False)
    response_text = Column(Text)