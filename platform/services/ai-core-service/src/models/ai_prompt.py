import uuid

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ..models.user import User
from .base import BaseModel, TimestampMixin


class AIPrompt(BaseModel, TimestampMixin):
    __tablename__ = "ai_prompts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(JSONB)
    temperature = Column(Float(precision=3, scale=2))
    max_tokens = Column(Integer)
    is_system = Column(Boolean, default=False)