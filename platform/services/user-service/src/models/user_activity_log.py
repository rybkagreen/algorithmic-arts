import uuid

from sqlalchemy import UUID, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ..models.user import User
from .base import BaseModel, TimestampMixin


class UserActivityLog(BaseModel):
    __tablename__ = "user_activity_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(PGUUID(as_uuid=True))
    metadata_ = Column(JSONB, name="metadata")
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)