import uuid

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ..models.ai_chat_session import AIChatSession
from .base import BaseModel, TimestampMixin


class AIChatMessage(BaseModel):
    __tablename__ = "ai_chat_messages"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("ai_chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    metadata_ = Column(JSONB, name="metadata")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)