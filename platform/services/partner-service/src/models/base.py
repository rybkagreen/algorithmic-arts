"""Base model for partner service."""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields."""
    __abstract__ = True
    
    @declared_attr
    def id(cls) -> Any:
        return Column("id", cls.id_type(), primary_key=True)
    
    @classmethod
    def id_type(cls) -> Any:
        from sqlalchemy.dialects.postgresql import UUID
        return UUID(as_uuid=True)