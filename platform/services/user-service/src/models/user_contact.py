import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel, TimestampMixin


class UserContact(BaseModel, TimestampMixin):
    __tablename__ = "user_contacts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    contact_type = Column(String(20), nullable=False)
    value = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)