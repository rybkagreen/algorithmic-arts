import uuid

from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ..models.user import User
from .base import BaseModel, TimestampMixin


class UserPreference(BaseModel, TimestampMixin):
    __tablename__ = "user_preferences"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(JSONB, nullable=False)