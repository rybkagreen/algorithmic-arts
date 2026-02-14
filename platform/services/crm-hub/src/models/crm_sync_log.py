import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel, TimestampMixin


class SyncDirection(str, PyEnum):
    TO_CRM = "to_crm"
    FROM_CRM = "from_crm"


class CRMSyncLog(BaseModel, TimestampMixin):
    __tablename__ = "crm_sync_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(PGUUID(as_uuid=True), nullable=False)
    direction = Column(Enum(SyncDirection), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    error_message = Column(Text)
    synced_at = Column(DateTime(timezone=True), nullable=False)