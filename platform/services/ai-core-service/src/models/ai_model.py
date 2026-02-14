import uuid

from sqlalchemy import (
    Boolean,
    Column,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel, TimestampMixin


class AIModel(BaseModel, TimestampMixin):
    __tablename__ = "ai_models"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False)
    model_id = Column(String(255), nullable=False)
    description = Column(Text)
    capabilities = Column(JSONB)
    is_active = Column(Boolean, default=True)