from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class CRMType(str, Enum):
    AMOCRM = "amocrm"
    BITRIX24 = "bitrix24"
    MEGAPLAN = "megaplan"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    PIPEDRIVE = "pipedrive"


@dataclass
class LeadData:
    """Унифицированная модель лида — не зависит от конкретной CRM."""

    title: str
    company_name: str
    contact_person: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    deal_value: int = 0  # в рублях
    compatibility_score: float = 0.0  # 0.0–1.0
    partnership_id: UUID | None = None
    status: str = "new"  # new | in_progress | won | lost
    notes: str | None = None
    external_id: str | None = None  # ID в CRM (заполняется после create)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ContactData:
    first_name: str
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    position: str | None = None
    external_id: str | None = None


@dataclass
class CRMConnection:
    id: UUID
    user_id: UUID
    crm_type: CRMType
    access_token: str  # расшифрованный (в памяти)
    refresh_token: str | None
    expires_at: datetime | None
    account_subdomain: str | None  # для amoCRM и Битрикс24
    account_id: str | None  # внешний идентификатор аккаунта


class BaseCRMAdapter(ABC):
    """
    Базовый класс для всех CRM-адаптеров.
    Все методы async. Токены передаются расшифрованными.
    """

    crm_type: CRMType

    def __init__(self, connection: CRMConnection):
        self.connection = connection

    # ─── OAuth ───────────────────────────────────────────────────────
    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str) -> CRMConnection:
        """Обменять authorization code на токены."""
        ...

    @abstractmethod
    async def refresh_access_token(self) -> CRMConnection:
        """Обновить access_token через refresh_token."""
        ...

    # ─── Лиды ────────────────────────────────────────────────────────
    @abstractmethod
    async def create_lead(self, lead: LeadData) -> str:
        """Создать лид, вернуть external_id."""
        ...

    @abstractmethod
    async def update_lead(self, external_id: str, updates: dict) -> bool:
        """Обновить лид по external_id."""
        ...

    @abstractmethod
    async def get_lead(self, external_id: str) -> LeadData:
        """Получить лид по external_id."""
        ...

    @abstractmethod
    async def list_leads(self, updated_since: datetime | None = None) -> list[LeadData]:
        """Получить все лиды (для синхронизации FROM_CRM)."""
        ...

    # ─── Контакты ────────────────────────────────────────────────────
    @abstractmethod
    async def create_contact(self, contact: ContactData) -> str: ...

    # ─── Вебхуки ─────────────────────────────────────────────────────
    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """Верифицировать подпись входящего вебхука. По умолчанию — True."""
        return True

    def parse_webhook_event(self, payload: dict) -> dict | None:
        """
        Разобрать входящий вебхук → нормализованное событие.
        Вернуть None если событие нерелевантно.
        """
        return None
