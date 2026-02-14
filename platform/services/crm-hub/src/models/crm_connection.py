import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import BaseModel, TimestampMixin


class CRMType(str, PyEnum):
    AMOCRM = "amocrm"
    BITRIX24 = "bitrix24"
    SALESFORCE = "salesforce"


class CRMConnection(BaseModel, TimestampMixin):
    __tablename__ = "crm_connections"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    crm_type = Column(Enum(CRMType), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    account_subdomain = Column(String(255))