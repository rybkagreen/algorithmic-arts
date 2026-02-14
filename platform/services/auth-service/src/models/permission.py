import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel, TimestampMixin


class Permission(BaseModel, TimestampMixin):
    __tablename__ = "permissions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)