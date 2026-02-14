import uuid

from sqlalchemy import Column, DateTime, String, Float, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel


class AIEmbedding(BaseModel):
    __tablename__ = "ai_embeddings"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(PGUUID(as_uuid=True), nullable=False)
    embedding = Column(ARRAY(Float))
    metadata_ = Column(JSONB, name="metadata")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)