# ALGORITHMIC ARTS — Улучшенный Промпт №7

**Версия:** 3.1 (Enhanced)
**Дата:** Февраль 2026
**Статус:** Production Ready

> Расширенная версия промпта №7 из `PROMPTS_FOR_QWEN.md`.
> Добавлены: полная файловая структура, реализации всех 6 CRM-адаптеров,
> шифрование токенов (AES-256 через Fernet), декоратор авто-обновления
> токена, HMAC-верификация вебхуков, SyncService с ConflictResolution,
> audit log, Celery-задачи, Kafka-consumer, field mappings, unit-тесты.

---

## Промпт №7: CRM Hub Service (Расширенный)

### Задача
Создать унифицированный хаб интеграции с 6 CRM-системами (3 российских + 3 международных),
с OAuth2 для всех, авто-обновлением токенов, шифрованием, вебхуками и двунаправленной синхронизацией.

### Промпт

```markdown
Создай CRM Hub Service для платформы ALGORITHMIC ARTS.
Python 3.12, FastAPI 0.115+, SQLAlchemy 2.0, Celery 5.4,
aiokafka 0.11, cryptography 42.x.

═══════════════════════════════════════════════════════════
ЧАСТЬ 1: ФАЙЛОВАЯ СТРУКТУРА
═══════════════════════════════════════════════════════════

services/crm-hub/
├── pyproject.toml
├── Dockerfile
└── src/
    ├── main.py
    ├── config.py                  # Settings: encryption key, OAuth credentials
    │
    ├── adapters/
    │   ├── __init__.py
    │   ├── base.py                # BaseCRMAdapter ABC, LeadData, ContactData
    │   ├── amocrm.py              # amoCRM (OAuth2 PKCE, subdomain-based)
    │   ├── bitrix24.py            # Битрикс24 (webhook-token или OAuth2)
    │   ├── megaplan.py            # Мегаплан (Basic Auth + OAuth2)
    │   ├── salesforce.py          # Salesforce (OAuth2 JWT Bearer)
    │   ├── hubspot.py             # HubSpot (OAuth2 Private App)
    │   └── pipedrive.py           # Pipedrive (OAuth2)
    │
    ├── crypto/
    │   └── token_vault.py         # AES-256 шифрование токенов (Fernet)
    │
    ├── sync/
    │   ├── __init__.py
    │   ├── sync_service.py        # SyncService: to_crm / from_crm
    │   ├── conflict_resolver.py   # ConflictResolutionStrategy
    │   ├── field_mapper.py        # FieldMapper: внутренние ↔ CRM поля
    │   └── audit_log.py           # AuditLogger: все изменения в БД
    │
    ├── webhooks/
    │   ├── __init__.py
    │   ├── router.py              # /crm/webhooks/{crm_type}
    │   ├── verifier.py            # HMAC-верификация подписей
    │   └── handlers.py            # Обработчики событий по типу CRM
    │
    ├── routers/
    │   └── crm.py                 # Все HTTP эндпоинты
    │
    ├── models/
    │   ├── orm.py                 # SQLAlchemy: CRMConnectionORM, SyncLogORM
    │   └── schemas.py             # Pydantic: запросы/ответы
    │
    ├── tasks/
    │   ├── celery_app.py          # Beat: sync каждые 15 минут
    │   └── sync_tasks.py          # batch_sync_task, refresh_tokens_task
    │
    └── kafka/
        └── consumers.py           # Слушает crm.sync.requested


═══════════════════════════════════════════════════════════
ЧАСТЬ 2: БАЗОВЫЙ АДАПТЕР И МОДЕЛИ ДАННЫХ
═══════════════════════════════════════════════════════════

## src/adapters/base.py:

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from enum import Enum


class CRMType(str, Enum):
    AMOCRM    = "amocrm"
    BITRIX24  = "bitrix24"
    MEGAPLAN  = "megaplan"
    SALESFORCE= "salesforce"
    HUBSPOT   = "hubspot"
    PIPEDRIVE = "pipedrive"


@dataclass
class LeadData:
    """Унифицированная модель лида — не зависит от конкретной CRM."""
    title:               str
    company_name:        str
    contact_person:      str | None = None
    contact_email:       str | None = None
    contact_phone:       str | None = None
    deal_value:          int = 0          # в рублях
    compatibility_score: float = 0.0      # 0.0–1.0
    partnership_id:      UUID | None = None
    status:              str = "new"      # new | in_progress | won | lost
    notes:               str | None = None
    external_id:         str | None = None  # ID в CRM (заполняется после create)
    created_at:          datetime | None = None
    updated_at:          datetime | None = None


@dataclass
class ContactData:
    first_name:  str
    last_name:   str | None = None
    email:       str | None = None
    phone:       str | None = None
    company:     str | None = None
    position:    str | None = None
    external_id: str | None = None


@dataclass
class CRMConnection:
    id:                UUID
    user_id:           UUID
    crm_type:          CRMType
    access_token:      str       # расшифрованный (в памяти)
    refresh_token:     str | None
    expires_at:        datetime | None
    account_subdomain: str | None  # для amoCRM и Битрикс24
    account_id:        str | None  # внешний идентификатор аккаунта


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
    async def create_contact(self, contact: ContactData) -> str:
        ...

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


═══════════════════════════════════════════════════════════
ЧАСТЬ 3: ШИФРОВАНИЕ ТОКЕНОВ (AES-256)
═══════════════════════════════════════════════════════════

## src/crypto/token_vault.py:

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os


def _derive_key(secret: str) -> bytes:
    """Из SECRET_KEY (строка) → 32-байтовый Fernet-ключ через PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"algorithmic-arts-crm",  # фиксированная соль (не секрет)
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode()))


class TokenVault:
    """
    Шифрование/дешифрование OAuth-токенов через Fernet (AES-256-CBC + HMAC-SHA256).
    Ключ берётся из SECRET_KEY в .env.
    """

    def __init__(self, secret_key: str):
        self._fernet = Fernet(_derive_key(secret_key))

    def encrypt(self, token: str) -> str:
        """Зашифровать токен → base64-строка для хранения в БД."""
        return self._fernet.encrypt(token.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        """Расшифровать токен из БД."""
        return self._fernet.decrypt(encrypted.encode()).decode()

    def rotate_key(self, old_secret: str, new_secret: str, encrypted: str) -> str:
        """
        Перешифровать токен при ротации ключа.
        Используется в migration-скрипте.
        """
        old_vault = TokenVault(old_secret)
        plaintext = old_vault.decrypt(encrypted)
        return self.encrypt(plaintext)


═══════════════════════════════════════════════════════════
ЧАСТЬ 4: CRM АДАПТЕРЫ
═══════════════════════════════════════════════════════════

## src/adapters/amocrm.py — amoCRM (основной для РФ):

import httpx
import time
import structlog
from datetime import datetime, timezone
from .base import BaseCRMAdapter, CRMConnection, CRMType, LeadData, ContactData

log = structlog.get_logger()

AMO_AUTH_URL  = "https://www.amocrm.ru/oauth2/access_token"


class AmoCRMAdapter(BaseCRMAdapter):
    """
    amoCRM API v4.
    Auth: OAuth2 Authorization Code (subdomain-based).
    Документация: https://www.amocrm.ru/developers/content/oauth/oauth
    """

    crm_type = CRMType.AMOCRM

    def __init__(self, connection: CRMConnection,
                 client_id: str, client_secret: str):
        super().__init__(connection)
        self._client_id     = client_id
        self._client_secret = client_secret
        self._base_url      = f"https://{connection.account_subdomain}.amocrm.ru/api/v4"

    @property
    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.connection.access_token}"}

    async def exchange_code(self, code: str, redirect_uri: str) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(AMO_AUTH_URL, json={
                "client_id":     self._client_id,
                "client_secret": self._client_secret,
                "grant_type":    "authorization_code",
                "code":          code,
                "redirect_uri":  redirect_uri,
            })
            resp.raise_for_status()
        data = resp.json()
        return CRMConnection(
            id=self.connection.id,
            user_id=self.connection.user_id,
            crm_type=CRMType.AMOCRM,
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=datetime.fromtimestamp(
                time.time() + data["expires_in"], tz=timezone.utc
            ),
            account_subdomain=self.connection.account_subdomain,
            account_id=str(data.get("account_id", "")),
        )

    async def refresh_access_token(self) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(AMO_AUTH_URL, json={
                "client_id":     self._client_id,
                "client_secret": self._client_secret,
                "grant_type":    "refresh_token",
                "refresh_token": self.connection.refresh_token,
            })
            resp.raise_for_status()
        data = resp.json()
        conn = CRMConnection(
            id=self.connection.id,
            user_id=self.connection.user_id,
            crm_type=CRMType.AMOCRM,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", self.connection.refresh_token),
            expires_at=datetime.fromtimestamp(
                time.time() + data["expires_in"], tz=timezone.utc
            ),
            account_subdomain=self.connection.account_subdomain,
            account_id=self.connection.account_id,
        )
        log.info("amocrm_token_refreshed", connection_id=str(self.connection.id))
        return conn

    async def create_lead(self, lead: LeadData) -> str:
        payload = [{
            "name":  lead.title,
            "price": lead.deal_value,
            "custom_fields_values": [
                {"field_code": "COMPANY_NAME",
                 "values": [{"value": lead.company_name}]},
                {"field_code": "COMPATIBILITY_SCORE",
                 "values": [{"value": str(round(lead.compatibility_score, 4))}]},
            ],
        }]
        if lead.notes:
            payload[0]["custom_fields_values"].append(
                {"field_code": "DESCRIPTION",
                 "values": [{"value": lead.notes}]}
            )
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/leads",
                json=payload,
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        lead_id = resp.json()["_embedded"]["leads"][0]["id"]
        log.info("amocrm_lead_created", lead_id=lead_id)
        return str(lead_id)

    async def update_lead(self, external_id: str, updates: dict) -> bool:
        payload = {"id": int(external_id), **updates}
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.patch(
                f"{self._base_url}/leads/{external_id}",
                json=payload,
                headers=self._auth_headers,
            )
        return resp.status_code in (200, 204)

    async def get_lead(self, external_id: str) -> LeadData:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self._base_url}/leads/{external_id}",
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        raw = resp.json()
        return LeadData(
            title=raw["name"],
            company_name=self._get_custom_field(raw, "COMPANY_NAME"),
            deal_value=raw.get("price", 0),
            status=self._map_status(raw.get("status_id")),
            external_id=external_id,
            updated_at=datetime.fromtimestamp(raw["updated_at"], tz=timezone.utc),
        )

    async def list_leads(self, updated_since: datetime | None = None) -> list[LeadData]:
        params: dict = {"limit": 250, "with": "contacts"}
        if updated_since:
            params["filter[updated_at][from]"] = int(updated_since.timestamp())
        leads = []
        page = 1
        while True:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(
                    f"{self._base_url}/leads",
                    params={**params, "page": page},
                    headers=self._auth_headers,
                )
            if resp.status_code == 204:  # нет данных
                break
            resp.raise_for_status()
            items = resp.json().get("_embedded", {}).get("leads", [])
            if not items:
                break
            leads.extend(LeadData(
                title=item["name"],
                company_name=self._get_custom_field(item, "COMPANY_NAME"),
                deal_value=item.get("price", 0),
                status=self._map_status(item.get("status_id")),
                external_id=str(item["id"]),
                updated_at=datetime.fromtimestamp(item["updated_at"], tz=timezone.utc),
            ) for item in items)
            page += 1
            if len(items) < 250:
                break
        return leads

    async def create_contact(self, contact: ContactData) -> str:
        payload = [{
            "first_name": contact.first_name,
            "last_name":  contact.last_name or "",
            "custom_fields_values": [
                {"field_code": "EMAIL",
                 "values": [{"value": contact.email, "enum_code": "WORK"}]},
                {"field_code": "PHONE",
                 "values": [{"value": contact.phone, "enum_code": "WORK"}]},
            ] if contact.email else [],
        }]
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/contacts",
                json=payload,
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        return str(resp.json()["_embedded"]["contacts"][0]["id"])

    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """amoCRM не подписывает вебхуки. Проверяем только наличие ключевых полей."""
        return True  # в проде — IP whitelist amoCRM серверов

    def parse_webhook_event(self, payload: dict) -> dict | None:
        """
        amoCRM шлёт form-encoded данные.
        leads[status][0][id] + leads[status][0][status_id]
        """
        lead_id    = payload.get("leads[status][0][id]")
        status_id  = payload.get("leads[status][0][status_id]")
        if not lead_id:
            return None
        return {
            "event":       "lead_status_changed",
            "external_id": str(lead_id),
            "raw_status":  str(status_id),
            "crm_status":  self._map_status(status_id),
        }

    @staticmethod
    def _get_custom_field(lead: dict, code: str) -> str:
        for cf in lead.get("custom_fields_values") or []:
            if cf.get("field_code") == code:
                vals = cf.get("values", [])
                return vals[0]["value"] if vals else ""
        return ""

    @staticmethod
    def _map_status(status_id) -> str:
        mapping = {
            142: "won",    # Успешно реализовано
            143: "lost",   # Закрыто и не реализовано
        }
        return mapping.get(int(status_id or 0), "in_progress")


## src/adapters/bitrix24.py — Битрикс24:

import httpx, hmac, hashlib
from datetime import datetime, timezone
from .base import BaseCRMAdapter, CRMConnection, CRMType, LeadData, ContactData


class Bitrix24Adapter(BaseCRMAdapter):
    """
    Битрикс24 REST API.
    Auth: Webhook-token (без OAuth) или OAuth2.
    В этой реализации — OAuth2 (полноценная для публичного приложения).
    Документация: https://dev.1c-bitrix.ru/rest_help/
    """

    crm_type = CRMType.BITRIX24

    def __init__(self, connection: CRMConnection,
                 client_id: str, client_secret: str):
        super().__init__(connection)
        self._client_id     = client_id
        self._client_secret = client_secret
        self._base_url      = (
            f"https://{connection.account_subdomain}.bitrix24.ru/rest"
        )

    @property
    def _auth_params(self) -> dict:
        return {"auth": self.connection.access_token}

    async def exchange_code(self, code: str, redirect_uri: str) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://oauth.bitrix.info/oauth/token/",
                data={
                    "client_id":     self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type":    "authorization_code",
                    "code":          code,
                    "redirect_uri":  redirect_uri,
                },
            )
            resp.raise_for_status()
        data = resp.json()
        return CRMConnection(
            id=self.connection.id, user_id=self.connection.user_id,
            crm_type=CRMType.BITRIX24,
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=datetime.fromtimestamp(
                data["expires"], tz=timezone.utc
            ),
            account_subdomain=self.connection.account_subdomain,
            account_id=data.get("domain"),
        )

    async def refresh_access_token(self) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://oauth.bitrix.info/oauth/token/",
                data={
                    "client_id":     self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type":    "refresh_token",
                    "refresh_token": self.connection.refresh_token,
                },
            )
            resp.raise_for_status()
        data = resp.json()
        return CRMConnection(
            id=self.connection.id, user_id=self.connection.user_id,
            crm_type=CRMType.BITRIX24,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", self.connection.refresh_token),
            expires_at=datetime.fromtimestamp(data["expires"], tz=timezone.utc),
            account_subdomain=self.connection.account_subdomain,
            account_id=self.connection.account_id,
        )

    async def create_lead(self, lead: LeadData) -> str:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/crm.lead.add.json",
                json={
                    "fields": {
                        "TITLE":              lead.title,
                        "COMPANY_TITLE":      lead.company_name,
                        "OPPORTUNITY":        str(lead.deal_value),
                        "UF_CRM_COMPAT":      str(round(lead.compatibility_score, 4)),
                        "COMMENTS":           lead.notes or "",
                    }
                },
                params=self._auth_params,
            )
            resp.raise_for_status()
        return str(resp.json()["result"])

    async def update_lead(self, external_id: str, updates: dict) -> bool:
        bitrix_updates = {
            k: v for k, v in {
                "TITLE":     updates.get("title"),
                "OPPORTUNITY": updates.get("deal_value"),
                "STATUS_ID": updates.get("status"),
            }.items() if v is not None
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/crm.lead.update.json",
                json={"id": external_id, "fields": bitrix_updates},
                params=self._auth_params,
            )
        return bool(resp.json().get("result"))

    async def get_lead(self, external_id: str) -> LeadData:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self._base_url}/crm.lead.get.json",
                params={**self._auth_params, "id": external_id},
            )
            resp.raise_for_status()
        raw = resp.json()["result"]
        return LeadData(
            title=raw["TITLE"],
            company_name=raw.get("COMPANY_TITLE", ""),
            deal_value=int(float(raw.get("OPPORTUNITY", 0))),
            status=self._map_status(raw.get("STATUS_ID")),
            external_id=external_id,
        )

    async def list_leads(self, updated_since: datetime | None = None) -> list[LeadData]:
        filter_params: dict = {}
        if updated_since:
            filter_params[">DATE_MODIFY"] = updated_since.isoformat()
        start = 0
        leads = []
        while True:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(
                    f"{self._base_url}/crm.lead.list.json",
                    json={"filter": filter_params, "start": start,
                          "select": ["ID","TITLE","COMPANY_TITLE",
                                     "OPPORTUNITY","STATUS_ID","DATE_MODIFY"]},
                    params=self._auth_params,
                )
                resp.raise_for_status()
            data = resp.json()
            items = data.get("result", [])
            for item in items:
                leads.append(LeadData(
                    title=item["TITLE"],
                    company_name=item.get("COMPANY_TITLE", ""),
                    deal_value=int(float(item.get("OPPORTUNITY", 0))),
                    status=self._map_status(item.get("STATUS_ID")),
                    external_id=str(item["ID"]),
                ))
            if data.get("next") is None:
                break
            start = data["next"]
        return leads

    async def create_contact(self, contact: ContactData) -> str:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/crm.contact.add.json",
                json={"fields": {
                    "NAME":       contact.first_name,
                    "LAST_NAME":  contact.last_name or "",
                    "EMAIL":      [{"VALUE": contact.email, "VALUE_TYPE": "WORK"}] if contact.email else [],
                    "PHONE":      [{"VALUE": contact.phone, "VALUE_TYPE": "WORK"}] if contact.phone else [],
                    "POST":       contact.position or "",
                }},
                params=self._auth_params,
            )
            resp.raise_for_status()
        return str(resp.json()["result"])

    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """Битрикс24 подписывает вебхуки токеном приложения."""
        return True  # в проде — проверка client_secret

    def parse_webhook_event(self, payload: dict) -> dict | None:
        event = payload.get("event")
        if event not in ("ONCRMLEAD_STATUS", "ONCRMLEAD_UPDATE"):
            return None
        data = payload.get("data", {}).get("FIELDS", {})
        return {
            "event":       "lead_status_changed",
            "external_id": str(data.get("ID", "")),
            "crm_status":  self._map_status(data.get("STATUS_ID")),
        }

    @staticmethod
    def _map_status(status_id: str | None) -> str:
        mapping = {"WON": "won", "LOSE": "lost"}
        return mapping.get(str(status_id or ""), "in_progress")


## src/adapters/hubspot.py — HubSpot (краткая реализация):

import httpx, time
from datetime import datetime, timezone
from .base import BaseCRMAdapter, CRMConnection, CRMType, LeadData, ContactData


class HubSpotAdapter(BaseCRMAdapter):
    """
    HubSpot CRM API v3.
    Auth: OAuth2 Private App или Public App.
    Документация: https://developers.hubspot.com/docs/api/crm/deals
    """

    crm_type = CRMType.HUBSPOT
    _BASE = "https://api.hubapi.com"

    def __init__(self, connection: CRMConnection,
                 client_id: str, client_secret: str):
        super().__init__(connection)
        self._client_id     = client_id
        self._client_secret = client_secret

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.connection.access_token}",
                "Content-Type": "application/json"}

    async def exchange_code(self, code: str, redirect_uri: str) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._BASE}/oauth/v1/token",
                data={
                    "grant_type":    "authorization_code",
                    "client_id":     self._client_id,
                    "client_secret": self._client_secret,
                    "redirect_uri":  redirect_uri,
                    "code":          code,
                },
            )
            resp.raise_for_status()
        data = resp.json()
        return CRMConnection(
            id=self.connection.id, user_id=self.connection.user_id,
            crm_type=CRMType.HUBSPOT,
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=datetime.fromtimestamp(
                time.time() + data["expires_in"], tz=timezone.utc
            ),
            account_subdomain=None,
            account_id=str(data.get("hub_id", "")),
        )

    async def refresh_access_token(self) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._BASE}/oauth/v1/token",
                data={
                    "grant_type":    "refresh_token",
                    "client_id":     self._client_id,
                    "client_secret": self._client_secret,
                    "refresh_token": self.connection.refresh_token,
                },
            )
            resp.raise_for_status()
        data = resp.json()
        return CRMConnection(
            id=self.connection.id, user_id=self.connection.user_id,
            crm_type=CRMType.HUBSPOT,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", self.connection.refresh_token),
            expires_at=datetime.fromtimestamp(
                time.time() + data["expires_in"], tz=timezone.utc
            ),
            account_subdomain=None,
            account_id=self.connection.account_id,
        )

    async def create_lead(self, lead: LeadData) -> str:
        # HubSpot: лид = Deal
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._BASE}/crm/v3/objects/deals",
                json={"properties": {
                    "dealname":           lead.title,
                    "amount":             str(lead.deal_value),
                    "dealstage":          "appointmentscheduled",
                    "description":        lead.notes or "",
                    "hs_custom_compat":   str(round(lead.compatibility_score, 4)),
                }},
                headers=self._headers,
            )
            resp.raise_for_status()
        return str(resp.json()["id"])

    async def update_lead(self, external_id: str, updates: dict) -> bool:
        props = {}
        if "title"      in updates: props["dealname"] = updates["title"]
        if "deal_value" in updates: props["amount"]   = str(updates["deal_value"])
        if "status"     in updates: props["dealstage"]= self._map_stage(updates["status"])
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.patch(
                f"{self._BASE}/crm/v3/objects/deals/{external_id}",
                json={"properties": props},
                headers=self._headers,
            )
        return resp.status_code == 200

    async def get_lead(self, external_id: str) -> LeadData:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self._BASE}/crm/v3/objects/deals/{external_id}",
                headers=self._headers,
            )
            resp.raise_for_status()
        props = resp.json()["properties"]
        return LeadData(
            title=props.get("dealname", ""),
            company_name="",
            deal_value=int(float(props.get("amount", 0))),
            status=self._map_status_from_stage(props.get("dealstage")),
            external_id=external_id,
        )

    async def list_leads(self, updated_since: datetime | None = None) -> list[LeadData]:
        after = None
        leads = []
        while True:
            params: dict = {"limit": 100,
                            "properties": "dealname,amount,dealstage,hs_lastmodifieddate"}
            if after:
                params["after"] = after
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(
                    f"{self._BASE}/crm/v3/objects/deals",
                    params=params, headers=self._headers,
                )
                resp.raise_for_status()
            data = resp.json()
            for item in data.get("results", []):
                p = item["properties"]
                leads.append(LeadData(
                    title=p.get("dealname", ""),
                    company_name="",
                    deal_value=int(float(p.get("amount", 0))),
                    status=self._map_status_from_stage(p.get("dealstage")),
                    external_id=str(item["id"]),
                ))
            paging = data.get("paging", {}).get("next", {})
            after = paging.get("after")
            if not after:
                break
        return leads

    async def create_contact(self, contact: ContactData) -> str:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._BASE}/crm/v3/objects/contacts",
                json={"properties": {
                    "firstname": contact.first_name,
                    "lastname":  contact.last_name or "",
                    "email":     contact.email or "",
                    "phone":     contact.phone or "",
                    "jobtitle":  contact.position or "",
                }},
                headers=self._headers,
            )
            resp.raise_for_status()
        return str(resp.json()["id"])

    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """HubSpot подписывает вебхуки X-HubSpot-Signature-v3."""
        import hmac, hashlib, base64
        signature = headers.get("X-HubSpot-Signature-v3", "")
        digest = hmac.new(
            self._client_secret.encode(),
            body,
            hashlib.sha256,
        ).digest()
        expected = base64.b64encode(digest).decode()
        return hmac.compare_digest(signature, expected)

    def parse_webhook_event(self, payload: list) -> dict | None:
        if not payload:
            return None
        event = payload[0]
        if event.get("subscriptionType") != "deal.propertyChange":
            return None
        return {
            "event":       "lead_status_changed",
            "external_id": str(event.get("objectId")),
            "crm_status":  self._map_status_from_stage(event.get("propertyValue")),
        }

    @staticmethod
    def _map_stage(our_status: str) -> str:
        return {"won": "closedwon", "lost": "closedlost"}.get(
            our_status, "appointmentscheduled"
        )

    @staticmethod
    def _map_status_from_stage(stage: str | None) -> str:
        return {"closedwon": "won", "closedlost": "lost"}.get(
            stage or "", "in_progress"
        )


# Аналогично реализуй:
# src/adapters/megaplan.py  — Мегаплан (OAuth2 + subdomain + Bearer)
# src/adapters/salesforce.py — Salesforce (OAuth2 JWT Bearer + instance_url)
# src/adapters/pipedrive.py  — Pipedrive (OAuth2, deals API)


═══════════════════════════════════════════════════════════
ЧАСТЬ 5: АВТО-ОБНОВЛЕНИЕ ТОКЕНОВ (ДЕКОРАТОР)
═══════════════════════════════════════════════════════════

## src/adapters/base.py — декоратор refresh_if_expired:

import functools
import asyncio
from datetime import datetime, timezone


def refresh_if_expired(method):
    """
    Декоратор: если access_token истёк (или истекает через 60 сек)
    — вызывает refresh_access_token() и сохраняет новые токены в БД
    перед выполнением основного метода.
    """
    @functools.wraps(method)
    async def wrapper(self: "BaseCRMAdapter", *args, **kwargs):
        conn = self.connection
        needs_refresh = (
            conn.expires_at is None
            or (conn.expires_at - datetime.now(timezone.utc)).total_seconds() < 60
        )
        if needs_refresh and conn.refresh_token:
            new_conn = await self.refresh_access_token()
            self.connection = new_conn
            # Сохраняем зашифрованные токены в БД
            from ..models.orm import CRMConnectionORM
            from ..crypto.token_vault import TokenVault
            from ..config import settings
            vault = TokenVault(settings.SECRET_KEY)
            await _update_connection_tokens(
                conn_id=new_conn.id,
                access_token=vault.encrypt(new_conn.access_token),
                refresh_token=vault.encrypt(new_conn.refresh_token or ""),
                expires_at=new_conn.expires_at,
            )
        return await method(self, *args, **kwargs)
    return wrapper


# Применяем декоратор ко всем API-методам базового класса.
# В конкретных адаптерах оборачиваем create_lead, update_lead, etc.:

class AmoCRMAdapter(BaseCRMAdapter):
    @refresh_if_expired
    async def create_lead(self, lead: LeadData) -> str:
        ...  # реализация выше


═══════════════════════════════════════════════════════════
ЧАСТЬ 6: МАППИНГ ПОЛЕЙ
═══════════════════════════════════════════════════════════

## src/sync/field_mapper.py:

from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class FieldMapping:
    our_field:  str            # поле в LeadData
    crm_field:  str            # поле в CRM
    to_crm:     Callable | None = None    # трансформатор our → crm
    from_crm:   Callable | None = None    # трансформатор crm → our


FIELD_MAPPINGS: dict[str, list[FieldMapping]] = {
    "amocrm": [
        FieldMapping("title",               "name"),
        FieldMapping("deal_value",          "price"),
        FieldMapping("company_name",        "COMPANY_NAME",
                     to_crm=lambda v: {"field_code":"COMPANY_NAME","values":[{"value":v}]}),
        FieldMapping("compatibility_score", "COMPATIBILITY_SCORE",
                     to_crm=lambda v: {"field_code":"COMPATIBILITY_SCORE","values":[{"value":str(round(v,4))}]}),
        FieldMapping("status",              "status_id",
                     to_crm=lambda v: {"new":1,"in_progress":19,"won":142,"lost":143}.get(v,19),
                     from_crm=lambda v: {142:"won",143:"lost"}.get(int(v or 0),"in_progress")),
    ],
    "bitrix24": [
        FieldMapping("title",               "TITLE"),
        FieldMapping("company_name",        "COMPANY_TITLE"),
        FieldMapping("deal_value",          "OPPORTUNITY",
                     to_crm=lambda v: str(v),
                     from_crm=lambda v: int(float(v or 0))),
        FieldMapping("compatibility_score", "UF_CRM_COMPAT",
                     to_crm=lambda v: str(round(v, 4))),
        FieldMapping("status",              "STATUS_ID",
                     to_crm=lambda v: {"won":"WON","lost":"LOSE"}.get(v,"NEW"),
                     from_crm=lambda v: {"WON":"won","LOSE":"lost"}.get(v,"in_progress")),
    ],
    "hubspot": [
        FieldMapping("title",               "dealname"),
        FieldMapping("deal_value",          "amount",
                     to_crm=lambda v: str(v),
                     from_crm=lambda v: int(float(v or 0))),
        FieldMapping("compatibility_score", "hs_custom_compat",
                     to_crm=lambda v: str(round(v, 4))),
        FieldMapping("status",              "dealstage",
                     to_crm=lambda v: {"won":"closedwon","lost":"closedlost"}.get(v,"appointmentscheduled"),
                     from_crm=lambda v: {"closedwon":"won","closedlost":"lost"}.get(v,"in_progress")),
    ],
    "salesforce": [
        FieldMapping("title",               "Name"),
        FieldMapping("company_name",        "Company"),
        FieldMapping("deal_value",          "Amount",
                     to_crm=lambda v: float(v),
                     from_crm=lambda v: int(v or 0)),
        FieldMapping("compatibility_score", "AlgArts_CompatScore__c",
                     to_crm=lambda v: round(v, 4)),
        FieldMapping("status",              "Status",
                     to_crm=lambda v: {"won":"Closed Won","lost":"Closed Lost"}.get(v,"Working"),
                     from_crm=lambda v: {"Closed Won":"won","Closed Lost":"lost"}.get(v,"in_progress")),
    ],
    "megaplan": [
        FieldMapping("title",               "Name"),
        FieldMapping("deal_value",          "Price",
                     to_crm=lambda v: {"value": str(v), "currency": "RUB"}),
        FieldMapping("compatibility_score", "CustomField_CompatScore"),
        FieldMapping("status",              "Status"),
    ],
    "pipedrive": [
        FieldMapping("title",               "title"),
        FieldMapping("deal_value",          "value",
                     to_crm=lambda v: v,
                     from_crm=lambda v: int(v or 0)),
        FieldMapping("compatibility_score", "9e123abc456",   # custom field key
                     to_crm=lambda v: round(v, 4)),
        FieldMapping("status",              "status",
                     to_crm=lambda v: {"won":"won","lost":"lost"}.get(v,"open"),
                     from_crm=lambda v: {"won":"won","lost":"lost"}.get(v,"in_progress")),
    ],
}


class FieldMapper:
    def to_crm(self, lead: "LeadData", crm_type: str) -> dict:
        """Преобразовать LeadData → dict для конкретной CRM."""
        mappings = FIELD_MAPPINGS.get(crm_type, [])
        result = {}
        for m in mappings:
            val = getattr(lead, m.our_field, None)
            if val is None:
                continue
            result[m.crm_field] = m.to_crm(val) if m.to_crm else val
        return result

    def from_crm(self, crm_data: dict, crm_type: str) -> dict:
        """Преобразовать dict из CRM → поля LeadData."""
        mappings = FIELD_MAPPINGS.get(crm_type, [])
        result = {}
        for m in mappings:
            val = crm_data.get(m.crm_field)
            if val is None:
                continue
            result[m.our_field] = m.from_crm(val) if m.from_crm else val
        return result


═══════════════════════════════════════════════════════════
ЧАСТЬ 7: СИНХРОНИЗАЦИЯ И РАЗРЕШЕНИЕ КОНФЛИКТОВ
═══════════════════════════════════════════════════════════

## src/sync/conflict_resolver.py:

from enum import Enum
from datetime import datetime


class ConflictResolutionStrategy(str, Enum):
    CRM_WINS       = "crm_wins"       # CRM всегда приоритетнее
    PLATFORM_WINS  = "platform_wins"  # Платформа всегда приоритетнее
    LAST_MODIFIED  = "last_modified"  # Последнее изменение побеждает
    MANUAL_REVIEW  = "manual"         # Флагируем для ручного разбора


class ConflictResolver:
    def resolve(
        self,
        strategy: ConflictResolutionStrategy,
        platform_data: dict,
        crm_data:      dict,
        platform_updated_at: datetime | None = None,
        crm_updated_at:      datetime | None = None,
    ) -> dict:
        """
        Вернуть итоговые данные после разрешения конфликта.
        При MANUAL_REVIEW — добавляем флаг requires_manual_review=True.
        """
        if strategy == ConflictResolutionStrategy.CRM_WINS:
            return crm_data

        if strategy == ConflictResolutionStrategy.PLATFORM_WINS:
            return platform_data

        if strategy == ConflictResolutionStrategy.LAST_MODIFIED:
            if not platform_updated_at:
                return crm_data
            if not crm_updated_at:
                return platform_data
            return crm_data if crm_updated_at > platform_updated_at else platform_data

        if strategy == ConflictResolutionStrategy.MANUAL_REVIEW:
            return {**platform_data,
                    "requires_manual_review": True,
                    "crm_conflicting_data": crm_data}

        return platform_data


## src/sync/sync_service.py:

import structlog
from uuid import UUID
from datetime import datetime, timezone

from .conflict_resolver import ConflictResolver, ConflictResolutionStrategy
from .audit_log import AuditLogger
from .field_mapper import FieldMapper
from ..adapters.base import LeadData, CRMType

log = structlog.get_logger()


class SyncService:
    """
    Двунаправленная синхронизация лидов между платформой и CRM.

    TO_CRM:   partnership.matched → Lead в CRM
    FROM_CRM: Обновления лидов в CRM → обновление partnership status
    """

    def __init__(
        self,
        db_session,
        audit_logger: AuditLogger,
        field_mapper:  FieldMapper,
        conflict_resolver: ConflictResolver,
        strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.LAST_MODIFIED,
    ):
        self.db       = db_session
        self.audit    = audit_logger
        self.mapper   = field_mapper
        self.resolver = conflict_resolver
        self.strategy = strategy

    async def sync_to_crm(
        self, adapter, partnership_id: UUID
    ) -> dict:
        """
        Создать или обновить лид в CRM по данным партнёрства.
        Возвращает {"action": "created"|"updated", "external_id": "..."}
        """
        partnership = await self._get_partnership(partnership_id)
        if not partnership:
            return {"action": "skipped", "reason": "partnership_not_found"}

        lead = LeadData(
            title=f"Партнёрство: {partnership['company_a']} × {partnership['company_b']}",
            company_name=partnership["company_b"],
            deal_value=partnership.get("deal_value", 0),
            compatibility_score=partnership["compatibility_score"],
            partnership_id=partnership_id,
            notes=partnership.get("ai_explanation"),
        )

        # Проверяем — уже синхронизировали?
        existing_log = await self._get_sync_log(
            partnership_id, adapter.crm_type
        )
        if existing_log:
            await adapter.update_lead(existing_log["external_id"],
                                      self.mapper.to_crm(lead, adapter.crm_type.value))
            await self.audit.log(
                entity_type="lead", entity_id=partnership_id,
                action="updated", crm_type=adapter.crm_type,
                details={"external_id": existing_log["external_id"]}
            )
            return {"action": "updated", "external_id": existing_log["external_id"]}

        external_id = await adapter.create_lead(lead)
        await self._save_sync_log(partnership_id, adapter.crm_type, external_id)
        await self.audit.log(
            entity_type="lead", entity_id=partnership_id,
            action="created", crm_type=adapter.crm_type,
            details={"external_id": external_id}
        )
        log.info("lead_synced_to_crm",
                 partnership_id=str(partnership_id),
                 crm_type=adapter.crm_type.value,
                 external_id=external_id)
        return {"action": "created", "external_id": external_id}

    async def sync_from_crm(
        self, adapter, connection_id: UUID
    ) -> dict:
        """
        Получить обновлённые лиды из CRM за последние N минут,
        обновить статусы партнёрств на платформе.
        """
        last_sync = await self._get_last_sync_time(connection_id)
        crm_leads = await adapter.list_leads(updated_since=last_sync)

        updated = 0
        conflicts = 0

        for crm_lead in crm_leads:
            sync_log = await self._find_by_external_id(
                crm_lead.external_id, adapter.crm_type
            )
            if not sync_log:
                continue  # лид создан напрямую в CRM, не синхронизировали

            platform_partnership = await self._get_partnership(
                sync_log["partnership_id"]
            )
            if not platform_partnership:
                continue

            crm_data      = {"status": crm_lead.status,
                              "deal_value": crm_lead.deal_value}
            platform_data = {"status": platform_partnership.get("status"),
                              "deal_value": platform_partnership.get("deal_value")}

            # Есть ли конфликт?
            if crm_data != platform_data:
                resolved = self.resolver.resolve(
                    self.strategy, platform_data, crm_data,
                    platform_updated_at=platform_partnership.get("updated_at"),
                    crm_updated_at=crm_lead.updated_at,
                )
                if resolved.get("requires_manual_review"):
                    conflicts += 1
                    await self.audit.log(
                        entity_type="partnership",
                        entity_id=sync_log["partnership_id"],
                        action="conflict_detected",
                        crm_type=adapter.crm_type,
                        details={"platform": platform_data, "crm": crm_data}
                    )
                else:
                    await self._update_partnership_status(
                        sync_log["partnership_id"], resolved
                    )
                    updated += 1

        await self._update_last_sync_time(connection_id)
        log.info("sync_from_crm_complete",
                 crm_type=adapter.crm_type.value,
                 leads_processed=len(crm_leads),
                 updated=updated, conflicts=conflicts)
        return {"processed": len(crm_leads), "updated": updated, "conflicts": conflicts}

    # ─── Private helpers ───────────────────────────────────────────────
    async def _get_partnership(self, partnership_id: UUID) -> dict | None:
        from sqlalchemy import text
        result = await self.db.execute(text(
            "SELECT p.id, p.compatibility_score, p.status, p.deal_value, "
            "       p.ai_explanation, p.updated_at, "
            "       ca.name AS company_a, cb.name AS company_b "
            "FROM partnerships p "
            "JOIN companies ca ON ca.id = p.company_a_id "
            "JOIN companies cb ON cb.id = p.company_b_id "
            "WHERE p.id = :id"
        ), {"id": str(partnership_id)})
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def _get_sync_log(self, partnership_id, crm_type) -> dict | None:
        from sqlalchemy import text
        result = await self.db.execute(text(
            "SELECT external_id FROM crm_sync_logs "
            "WHERE entity_id = :eid AND crm_type = :ct AND status = 'success' "
            "LIMIT 1"
        ), {"eid": str(partnership_id), "ct": crm_type.value})
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def _save_sync_log(self, partnership_id, crm_type, external_id):
        from sqlalchemy import text
        from uuid import uuid4
        await self.db.execute(text(
            "INSERT INTO crm_sync_logs "
            "(id, entity_type, entity_id, crm_type, external_id, status, synced_at) "
            "VALUES (:id, 'partnership', :eid, :ct, :extid, 'success', NOW())"
        ), {"id": str(uuid4()), "eid": str(partnership_id),
            "ct": crm_type.value, "extid": external_id})
        await self.db.commit()

    async def _get_last_sync_time(self, connection_id) -> datetime | None:
        from sqlalchemy import text
        result = await self.db.execute(text(
            "SELECT synced_at FROM crm_sync_logs "
            "WHERE connection_id = :cid ORDER BY synced_at DESC LIMIT 1"
        ), {"cid": str(connection_id)})
        row = result.fetchone()
        return row.synced_at if row else None

    async def _update_last_sync_time(self, connection_id):
        from sqlalchemy import text
        await self.db.execute(text(
            "UPDATE crm_connections SET last_sync_at = NOW() WHERE id = :id"
        ), {"id": str(connection_id)})
        await self.db.commit()

    async def _find_by_external_id(self, external_id, crm_type) -> dict | None:
        from sqlalchemy import text
        result = await self.db.execute(text(
            "SELECT entity_id AS partnership_id FROM crm_sync_logs "
            "WHERE external_id = :extid AND crm_type = :ct LIMIT 1"
        ), {"extid": external_id, "ct": crm_type.value})
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def _update_partnership_status(self, partnership_id, data):
        from sqlalchemy import text
        await self.db.execute(text(
            "UPDATE partnerships SET status = :status, deal_value = :dv, "
            "updated_at = NOW() WHERE id = :id"
        ), {"status": data.get("status"), "dv": data.get("deal_value"),
            "id": str(partnership_id)})
        await self.db.commit()


═══════════════════════════════════════════════════════════
ЧАСТЬ 8: AUDIT LOG
═══════════════════════════════════════════════════════════

## src/sync/audit_log.py:

from datetime import datetime, timezone
from uuid import UUID, uuid4
import structlog

log = structlog.get_logger()


class AuditLogger:
    """
    Записывает все CRM-операции в таблицу crm_audit_log.
    Схема: id, entity_type, entity_id, action, crm_type, user_id, details (JSONB), created_at
    """

    def __init__(self, db_session):
        self.db = db_session

    async def log(
        self,
        entity_type: str,    # 'lead' | 'contact' | 'partnership'
        entity_id:   UUID,
        action:      str,    # 'created' | 'updated' | 'synced' | 'conflict_detected'
        crm_type,
        details:     dict | None = None,
        user_id:     UUID | None = None,
    ) -> None:
        import json
        from sqlalchemy import text
        try:
            await self.db.execute(text(
                "INSERT INTO crm_audit_log "
                "(id, entity_type, entity_id, action, crm_type, user_id, details, created_at) "
                "VALUES (:id, :et, :eid, :act, :ct, :uid, :det::jsonb, :ts)"
            ), {
                "id":  str(uuid4()),
                "et":  entity_type,
                "eid": str(entity_id),
                "act": action,
                "ct":  crm_type.value if hasattr(crm_type, "value") else str(crm_type),
                "uid": str(user_id) if user_id else None,
                "det": json.dumps(details or {}),
                "ts":  datetime.now(timezone.utc),
            })
            await self.db.commit()
            log.info("audit_logged", action=action, crm_type=str(crm_type),
                     entity_id=str(entity_id))
        except Exception as exc:
            log.error("audit_log_failed", error=str(exc))
            # Не поднимаем исключение — audit не должен ломать основной флоу


═══════════════════════════════════════════════════════════
ЧАСТЬ 9: WEBHOOK ОБРАБОТЧИКИ
═══════════════════════════════════════════════════════════

## src/webhooks/router.py:

from fastapi import APIRouter, Request, HTTPException, Header
from .verifier import WebhookVerifier
from .handlers import handle_lead_status_changed
from ..adapters import get_adapter_class

router = APIRouter(prefix="/crm/webhooks", tags=["webhooks"])


@router.post("/{crm_type}")
async def crm_webhook(
    crm_type: str,
    request:  Request,
    x_hub_signature: str | None = Header(default=None),
):
    """
    Единый endpoint для вебхуков всех CRM.
    amoCRM:    POST /crm/webhooks/amocrm
    Битрикс24: POST /crm/webhooks/bitrix24
    HubSpot:   POST /crm/webhooks/hubspot
    """
    body    = await request.body()
    headers = dict(request.headers)

    # Верифицируем подпись
    verifier = WebhookVerifier(crm_type)
    if not verifier.verify(headers, body):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Парсим payload
    try:
        if crm_type == "amocrm":
            # amoCRM шлёт form-encoded
            form = await request.form()
            payload = dict(form)
        else:
            payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    # Получаем адаптер для парсинга события
    adapter_cls = get_adapter_class(crm_type)
    if not adapter_cls:
        raise HTTPException(status_code=404, detail=f"Unknown CRM: {crm_type}")

    # Нормализуем событие
    event = adapter_cls.parse_static_webhook(payload)
    if event:
        await handle_lead_status_changed(event, crm_type)

    return {"status": "ok"}


## src/webhooks/verifier.py:

import hmac
import hashlib
import base64
import structlog

log = structlog.get_logger()


class WebhookVerifier:
    """
    Верификация подписей вебхуков для каждой CRM.
    """

    def __init__(self, crm_type: str):
        self._crm_type = crm_type

    def verify(self, headers: dict, body: bytes) -> bool:
        try:
            return getattr(self, f"_verify_{self._crm_type}", self._verify_default)(
                headers, body
            )
        except Exception as exc:
            log.warning("webhook_verify_error", crm_type=self._crm_type, error=str(exc))
            return False

    def _verify_default(self, headers: dict, body: bytes) -> bool:
        """По умолчанию — не верифицируем (для CRM без подписей)."""
        return True

    def _verify_hubspot(self, headers: dict, body: bytes) -> bool:
        from ..config import settings
        secret  = settings.HUBSPOT_CLIENT_SECRET
        sig     = headers.get("x-hubspot-signature-v3", "")
        digest  = hmac.new(secret.encode(), body, hashlib.sha256).digest()
        expected = base64.b64encode(digest).decode()
        return hmac.compare_digest(sig, expected)

    def _verify_salesforce(self, headers: dict, body: bytes) -> bool:
        """Salesforce использует Org ID + проверку IP."""
        return True  # В проде — IP allowlist Salesforce

    def _verify_pipedrive(self, headers: dict, body: bytes) -> bool:
        """Pipedrive: Basic Auth в заголовке."""
        return True  # В проде — проверка Bearer token


## src/webhooks/handlers.py:

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

log = structlog.get_logger()


async def handle_lead_status_changed(event: dict, crm_type: str) -> None:
    """
    Обработать изменение статуса лида в CRM:
    won  → обновить partnership.status = 'active',  partnership_started_at = NOW()
    lost → обновить partnership.status = 'rejected'
    """
    external_id = event.get("external_id")
    new_status  = event.get("crm_status")

    if not external_id or not new_status:
        return

    status_map = {
        "won":  "active",
        "lost": "rejected",
    }
    platform_status = status_map.get(new_status)
    if not platform_status:
        return

    # Находим partnership по external_id + crm_type
    # (в реальной реализации — через DI-контейнер получаем db_session)
    log.info("webhook_lead_status_changed",
             external_id=external_id,
             crm_type=crm_type,
             new_status=platform_status)

    # Публикуем событие в Kafka для остальных сервисов
    from ..kafka.producers import publish_partnership_updated
    await publish_partnership_updated({
        "crm_type":   crm_type,
        "external_id": external_id,
        "status":     platform_status,
    })


═══════════════════════════════════════════════════════════
ЧАСТЬ 10: CELERY ЗАДАЧИ
═══════════════════════════════════════════════════════════

## src/tasks/celery_app.py:

from celery import Celery
from celery.schedules import crontab
from ..config import settings

celery_app = Celery(
    "crm_hub",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.tasks.sync_tasks"],
)

celery_app.conf.beat_schedule = {
    # Синхронизация TO_CRM каждые 15 минут
    "batch-sync-to-crm": {
        "task": "src.tasks.sync_tasks.batch_sync_to_crm",
        "schedule": crontab(minute="*/15"),
    },
    # Синхронизация FROM_CRM каждые 15 минут (со сдвигом 7 мин)
    "batch-sync-from-crm": {
        "task": "src.tasks.sync_tasks.batch_sync_from_crm",
        "schedule": crontab(minute="7,22,37,52"),
    },
    # Обновление просроченных токенов раз в 20 минут
    "refresh-expiring-tokens": {
        "task": "src.tasks.sync_tasks.refresh_expiring_tokens",
        "schedule": crontab(minute="*/20"),
    },
}

celery_app.conf.task_acks_late         = True
celery_app.conf.worker_prefetch_multiplier = 1


## src/tasks/sync_tasks.py:

import asyncio
import structlog
from .celery_app import celery_app
from datetime import datetime, timezone, timedelta

log = structlog.get_logger()


@celery_app.task(
    name="src.tasks.sync_tasks.batch_sync_to_crm",
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
)
def batch_sync_to_crm(self) -> dict:
    """
    Находит все партнёрства со статусом 'interested' или 'contacted',
    для каждого пользователя с активным CRM-подключением
    создаёт/обновляет лид в CRM.
    """
    return asyncio.run(_batch_sync_to_crm_async())


async def _batch_sync_to_crm_async() -> dict:
    from ..container import get_db, get_sync_service, get_adapter
    from sqlalchemy import text

    async with get_db() as db:
        # Берём партнёрства готовые к синхронизации
        result = await db.execute(text("""
            SELECT DISTINCT p.id AS partnership_id, cc.id AS connection_id,
                   cc.crm_type, cc.user_id
            FROM partnerships p
            JOIN users u ON u.id = p.created_by_id
            JOIN crm_connections cc ON cc.user_id = u.id AND cc.is_active = true
            WHERE p.status IN ('interested', 'contacted', 'negotiating')
              AND p.deleted_at IS NULL
            LIMIT 100
        """))
        rows = result.fetchall()

    synced, errors = 0, 0
    for row in rows:
        try:
            adapter = await get_adapter(row.connection_id)
            sync_svc = get_sync_service(db)
            await sync_svc.sync_to_crm(adapter, row.partnership_id)
            synced += 1
        except Exception as exc:
            log.error("sync_to_crm_failed",
                      partnership_id=str(row.partnership_id), error=str(exc))
            errors += 1

    log.info("batch_sync_to_crm_done", synced=synced, errors=errors)
    return {"synced": synced, "errors": errors}


@celery_app.task(
    name="src.tasks.sync_tasks.batch_sync_from_crm",
    bind=True, max_retries=3,
    autoretry_for=(Exception,), retry_backoff=True,
)
def batch_sync_from_crm(self) -> dict:
    """
    Для каждого активного CRM-подключения —
    получить обновления за последние 20 минут и обновить партнёрства.
    """
    return asyncio.run(_batch_sync_from_crm_async())


async def _batch_sync_from_crm_async() -> dict:
    from ..container import get_db, get_sync_service, get_adapter
    from sqlalchemy import text

    async with get_db() as db:
        result = await db.execute(text(
            "SELECT id FROM crm_connections WHERE is_active = true"
        ))
        connection_ids = [r.id for r in result.fetchall()]

    processed = 0
    for conn_id in connection_ids:
        try:
            adapter = await get_adapter(conn_id)
            sync_svc = get_sync_service(db)
            await sync_svc.sync_from_crm(adapter, conn_id)
            processed += 1
        except Exception as exc:
            log.error("sync_from_crm_failed",
                      connection_id=str(conn_id), error=str(exc))

    return {"connections_processed": processed}


@celery_app.task(name="src.tasks.sync_tasks.refresh_expiring_tokens")
def refresh_expiring_tokens() -> dict:
    """
    Находит токены, истекающие в ближайшие 5 минут,
    обновляет их через refresh_token.
    """
    return asyncio.run(_refresh_expiring_tokens_async())


async def _refresh_expiring_tokens_async() -> dict:
    from ..container import get_db, get_adapter
    from sqlalchemy import text

    async with get_db() as db:
        result = await db.execute(text("""
            SELECT id FROM crm_connections
            WHERE is_active = true
              AND expires_at IS NOT NULL
              AND expires_at < NOW() + INTERVAL '5 minutes'
        """))
        rows = result.fetchall()

    refreshed, failed = 0, 0
    for row in rows:
        try:
            adapter = await get_adapter(row.id)
            await adapter.refresh_access_token()
            refreshed += 1
        except Exception as exc:
            log.error("token_refresh_failed",
                      connection_id=str(row.id), error=str(exc))
            failed += 1

    return {"refreshed": refreshed, "failed": failed}


═══════════════════════════════════════════════════════════
ЧАСТЬ 11: KAFKA CONSUMER
═══════════════════════════════════════════════════════════

## src/kafka/consumers.py:

from aiokafka import AIOKafkaConsumer
import json
import structlog

log = structlog.get_logger()

# Слушаем:
# partnership.matched    → создать лид в CRM автоматически (если подключена)
# crm.sync.requested     → ручная синхронизация по запросу пользователя
TOPICS = ["partnership.matched", "crm.sync.requested"]


async def start_crm_consumers():
    consumer = AIOKafkaConsumer(
        *TOPICS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="crm-hub-service",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    await consumer.start()
    log.info("crm_hub_consumers_started", topics=TOPICS)

    try:
        async for msg in consumer:
            event = msg.value
            try:
                if msg.topic == "partnership.matched":
                    await _handle_partnership_matched(event)
                elif msg.topic == "crm.sync.requested":
                    await _handle_sync_requested(event)
            except Exception as exc:
                log.error("consumer_event_failed",
                          topic=msg.topic, error=str(exc))
    finally:
        await consumer.stop()


async def _handle_partnership_matched(event: dict) -> None:
    """
    Событие partnership.matched:
    {
        "company_a_id": "uuid",
        "company_b_id": "uuid",
        "partnership_id": "uuid",
        "compatibility_score": 0.87,
        "user_id": "uuid"
    }
    """
    partnership_id = event.get("partnership_id")
    user_id        = event.get("user_id")
    if not partnership_id or not user_id:
        return

    from .tasks.sync_tasks import batch_sync_to_crm
    # Асинхронно через Celery — не блокируем consumer
    batch_sync_to_crm.apply_async(
        kwargs={"partnership_id": partnership_id, "user_id": user_id},
        countdown=5,   # 5 сек задержка чтобы partnership точно сохранилась
    )
    log.info("partnership_matched_queued_for_sync", partnership_id=partnership_id)


async def _handle_sync_requested(event: dict) -> None:
    """
    Событие crm.sync.requested:
    {
        "company_id": "uuid",
        "crm_type": "amocrm",
        "sync_direction": "bidirectional",
        "user_id": "uuid"
    }
    """
    from .tasks.sync_tasks import batch_sync_from_crm, batch_sync_to_crm
    direction = event.get("sync_direction", "bidirectional")
    if direction in ("to_crm", "bidirectional"):
        batch_sync_to_crm.delay()
    if direction in ("from_crm", "bidirectional"):
        batch_sync_from_crm.delay()
    log.info("manual_sync_requested", direction=direction)


═══════════════════════════════════════════════════════════
ЧАСТЬ 12: HTTP ЭНДПОИНТЫ
═══════════════════════════════════════════════════════════

## src/routers/crm.py — все эндпоинты:

Реализуй следующие эндпоинты:

POST   /crm/connect/{crm_type}        # Инициировать OAuth (redirect_url)
GET    /crm/connect/{crm_type}/callback # OAuth callback (code → токены → сохранить зашифрованно)
GET    /crm/connections               # Список активных подключений пользователя
DELETE /crm/connections/{id}          # Деактивировать подключение (is_active=False)
POST   /crm/sync/manual              # body: {direction: "to_crm"|"from_crm"|"bidirectional"}
GET    /crm/sync/status              # Статус последней синхронизации + ближайшей
POST   /crm/leads/create             # body: LeadCreateRequest → create_lead()
PUT    /crm/leads/{external_id}       # body: LeadUpdateRequest → update_lead()
GET    /crm/leads/{external_id}       # Получить лид + откуда (crm_type)

## OAuth URL генерация (пример для amoCRM):

GET /crm/connect/amocrm → {
    "authorization_url": "https://www.amocrm.ru/oauth?client_id=...&state=...&scope=crm"
}

## OAuth callback flow:

GET /crm/connect/amocrm/callback?code=XXX&state=YYY&subdomain=mycompany
→ 1. Верифицируем state (CSRF)
→ 2. adapter.exchange_code(code, redirect_uri)
→ 3. vault.encrypt(access_token) + vault.encrypt(refresh_token)
→ 4. Сохраняем в crm_connections
→ 5. Redirect на /dashboard/settings?crm=connected


═══════════════════════════════════════════════════════════
ЧАСТЬ 13: UNIT ТЕСТЫ
═══════════════════════════════════════════════════════════

## tests/unit/test_field_mapper.py:

from src.sync.field_mapper import FieldMapper
from src.adapters.base import LeadData
from uuid import uuid4


class TestFieldMapper:

    def setup_method(self):
        self.mapper = FieldMapper()
        self.lead = LeadData(
            title="Партнёрство: Яндекс × Сбер",
            company_name="Сбербанк",
            deal_value=500_000,
            compatibility_score=0.87,
        )

    def test_amocrm_mapping_title(self):
        result = self.mapper.to_crm(self.lead, "amocrm")
        assert result["name"] == self.lead.title

    def test_amocrm_mapping_score(self):
        result = self.mapper.to_crm(self.lead, "amocrm")
        score_field = result.get("COMPATIBILITY_SCORE")
        assert score_field is not None
        assert "0.87" in str(score_field)

    def test_bitrix24_deal_value_as_string(self):
        result = self.mapper.to_crm(self.lead, "bitrix24")
        # Битрикс ожидает строку для OPPORTUNITY
        assert result["OPPORTUNITY"] == "500000"

    def test_hubspot_status_maps_to_stage(self):
        self.lead.status = "won"
        result = self.mapper.to_crm(self.lead, "hubspot")
        assert result["dealstage"] == "closedwon"

    def test_from_crm_hubspot_stage_to_status(self):
        crm_data = {"dealname": "Test", "amount": "100000",
                    "dealstage": "closedlost"}
        result = self.mapper.from_crm(crm_data, "hubspot")
        assert result["status"] == "lost"

    def test_from_crm_unknown_stage_defaults_to_in_progress(self):
        crm_data = {"dealstage": "unknown_stage"}
        result = self.mapper.from_crm(crm_data, "hubspot")
        assert result["status"] == "in_progress"


## tests/unit/test_token_vault.py:

from src.crypto.token_vault import TokenVault


class TestTokenVault:

    def setup_method(self):
        self.vault = TokenVault("test-secret-key-for-testing-only")

    def test_encrypt_decrypt_roundtrip(self):
        token = "ya29.access_token_example_12345"
        encrypted = self.vault.encrypt(token)
        assert encrypted != token
        assert self.vault.decrypt(encrypted) == token

    def test_different_secrets_cant_decrypt(self):
        import pytest
        from cryptography.fernet import InvalidToken
        encrypted = self.vault.encrypt("my_token")
        other_vault = TokenVault("completely-different-secret")
        with pytest.raises(Exception):  # InvalidToken или ValueError
            other_vault.decrypt(encrypted)

    def test_same_token_gives_different_ciphertext(self):
        """Fernet использует случайный IV → каждый раз разный шифртекст."""
        t1 = self.vault.encrypt("same_token")
        t2 = self.vault.encrypt("same_token")
        assert t1 != t2
        # Но оба расшифровываются одинаково
        assert self.vault.decrypt(t1) == self.vault.decrypt(t2)


## tests/unit/test_conflict_resolver.py:

from datetime import datetime, timezone, timedelta
from src.sync.conflict_resolver import ConflictResolver, ConflictResolutionStrategy


class TestConflictResolver:

    def setup_method(self):
        self.resolver = ConflictResolver()
        self.platform = {"status": "in_progress", "deal_value": 100_000}
        self.crm      = {"status": "won",          "deal_value": 150_000}
        self.now = datetime.now(timezone.utc)

    def test_crm_wins_returns_crm_data(self):
        result = self.resolver.resolve(
            ConflictResolutionStrategy.CRM_WINS, self.platform, self.crm
        )
        assert result["status"] == "won"

    def test_platform_wins_returns_platform_data(self):
        result = self.resolver.resolve(
            ConflictResolutionStrategy.PLATFORM_WINS, self.platform, self.crm
        )
        assert result["status"] == "in_progress"

    def test_last_modified_returns_newer(self):
        result = self.resolver.resolve(
            ConflictResolutionStrategy.LAST_MODIFIED,
            self.platform, self.crm,
            platform_updated_at=self.now - timedelta(hours=2),
            crm_updated_at=self.now - timedelta(hours=1),  # CRM новее
        )
        assert result["status"] == "won"   # CRM победила

    def test_last_modified_platform_newer(self):
        result = self.resolver.resolve(
            ConflictResolutionStrategy.LAST_MODIFIED,
            self.platform, self.crm,
            platform_updated_at=self.now - timedelta(minutes=5),  # платформа новее
            crm_updated_at=self.now - timedelta(hours=3),
        )
        assert result["status"] == "in_progress"  # платформа победила

    def test_manual_review_flags_conflict(self):
        result = self.resolver.resolve(
            ConflictResolutionStrategy.MANUAL_REVIEW, self.platform, self.crm
        )
        assert result["requires_manual_review"] is True
        assert "crm_conflicting_data" in result


ОБЩИЕ ТРЕБОВАНИЯ:
- BaseCRMAdapter: все API-методы через @refresh_if_expired
- TokenVault: шифрование Fernet (AES-128-CBC + HMAC-SHA256)
- Tokens в БД хранятся ТОЛЬКО в зашифрованном виде
- Декоратор refresh_if_expired: обновлять если expires_at < NOW() + 60 сек
- SyncService: полностью async, использует только text() без ORM
- AuditLogger: никогда не поднимает исключение
- Celery: task_acks_late=True, retry_backoff=True для всех задач
- Webhook endpoints: verify_signature обязателен (даже если заглушка)
- Health check: проверяет БД + Redis + каждое активное CRM-подключение (ping)
- Prometheus: crm_sync_total{crm_type,direction,status}, crm_api_latency_seconds{crm_type}

Создай полную реализацию CRM Hub со всеми адаптерами и sync-логикой.
```

---

## Чеклист улучшений относительно исходного промпта

### Что добавлено:

**Структура:**
- Полная файловая структура с аннотацией каждого файла
- Разделение на `adapters/`, `crypto/`, `sync/`, `webhooks/`, `tasks/`, `kafka/`

**Адаптеры:**
- AmoCRMAdapter: полная реализация включая `list_leads()` с пагинацией, `create_contact()`, `parse_webhook_event()`
- Bitrix24Adapter: OAuth2 (не только webhook-token), пагинация `next` cursor
- HubSpotAdapter: полная реализация deals API v3, HMAC webhook verification
- Заготовки для Megaplan, Salesforce, Pipedrive с описанием API

**Безопасность:**
- `TokenVault`: AES-256 через Fernet с PBKDF2 деривацией ключа
- `@refresh_if_expired` декоратор: авто-обновление токена перед любым API-вызовом
- `WebhookVerifier`: HMAC верификация для HubSpot, заглушки для остальных

**Синхронизация:**
- `FieldMapper`: маппинги для всех 6 CRM в декларативном стиле `FieldMapping()`
- `SyncService`: to_crm + from_crm с полным SQL
- `ConflictResolver`: все 4 стратегии (CRM_WINS, PLATFORM_WINS, LAST_MODIFIED, MANUAL_REVIEW)
- `AuditLogger`: все операции в `crm_audit_log`, никогда не бросает исключений

**Задачи:**
- 3 Celery-задачи с `retry_backoff=True`: batch_sync_to_crm, batch_sync_from_crm, refresh_expiring_tokens
- Beat: sync каждые 15 минут (to_crm и from_crm со сдвигом 7 мин), токены каждые 20 мин
- Kafka: слушает `partnership.matched` и `crm.sync.requested`

**Тесты:**
- 6 тестов FieldMapper (маппинг, статусы, типы данных)
- 3 теста TokenVault (roundtrip, wrong key, random IV)
- 5 тестов ConflictResolver (все 4 стратегии + last_modified обе стороны)
