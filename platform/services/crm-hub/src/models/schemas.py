from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class CRMType(str, Enum):
    AMOCRM = "amocrm"
    BITRIX24 = "bitrix24"
    MEGAPLAN = "megaplan"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    PIPEDRIVE = "pipedrive"


class LeadData(BaseModel):
    """Унифицированная модель лида — не зависит от конкретной CRM."""

    title: str
    company_name: str
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    deal_value: int = 0  # в рублях
    compatibility_score: float = 0.0  # 0.0–1.0
    partnership_id: Optional[UUID] = None
    status: str = "new"  # new | in_progress | won | lost
    notes: Optional[str] = None
    external_id: Optional[str] = None  # ID в CRM (заполняется после create)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContactData(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    external_id: Optional[str] = None


class CRMConnectionCreate(BaseModel):
    crm_type: CRMType
    account_subdomain: Optional[str] = None
    client_id: str
    client_secret: str
    redirect_uri: str


class CRMConnectionResponse(BaseModel):
    id: UUID
    user_id: UUID
    crm_type: CRMType
    account_subdomain: Optional[str] = None
    account_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class SyncLog(BaseModel):
    id: UUID
    connection_id: UUID
    sync_type: str  # to_crm, from_crm
    external_id: Optional[str] = None
    internal_id: Optional[str] = None
    status: str  # success, failure
    error_message: Optional[str] = None
    created_at: datetime


class WebhookRequest(BaseModel):
    crm_type: CRMType
    headers: Dict[str, str]
    body: str


class TokenRefreshRequest(BaseModel):
    connection_id: UUID
    refresh_token: str
