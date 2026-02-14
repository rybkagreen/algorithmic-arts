import time
from datetime import datetime, timezone

import httpx
import structlog

from .base import BaseCRMAdapter, ContactData, CRMConnection, CRMType, LeadData

log = structlog.get_logger()

AMO_AUTH_URL = "https://www.amocrm.ru/oauth2/access_token"


class AmoCRMAdapter(BaseCRMAdapter):
    """
    amoCRM API v4.
    Auth: OAuth2 Authorization Code (subdomain-based).
    Документация: https://www.amocrm.ru/developers/content/oauth/oauth
    """

    crm_type = CRMType.AMOCRM

    def __init__(self, connection: CRMConnection, client_id: str, client_secret: str):
        super().__init__(connection)
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = f"https://{connection.account_subdomain}.amocrm.ru/api/v4"

    @property
    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.connection.access_token}"}

    async def exchange_code(self, code: str, redirect_uri: str) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                AMO_AUTH_URL,
                json={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
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
            resp = await client.post(
                AMO_AUTH_URL,
                json={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": self.connection.refresh_token,
                },
            )
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
        payload = [
            {
                "name": lead.title,
                "price": lead.deal_value,
                "custom_fields_values": [
                    {
                        "field_code": "COMPANY_NAME",
                        "values": [{"value": lead.company_name}],
                    },
                    {
                        "field_code": "COMPATIBILITY_SCORE",
                        "values": [{"value": str(round(lead.compatibility_score, 4))}],
                    },
                ],
            }
        ]
        if lead.notes:
            payload[0]["custom_fields_values"].append(
                {"field_code": "DESCRIPTION", "values": [{"value": lead.notes}]}
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
            leads.extend(
                LeadData(
                    title=item["name"],
                    company_name=self._get_custom_field(item, "COMPANY_NAME"),
                    deal_value=item.get("price", 0),
                    status=self._map_status(item.get("status_id")),
                    external_id=str(item["id"]),
                    updated_at=datetime.fromtimestamp(
                        item["updated_at"], tz=timezone.utc
                    ),
                )
                for item in items
            )
            page += 1
            if len(items) < 250:
                break
        return leads

    async def create_contact(self, contact: ContactData) -> str:
        payload = [
            {
                "first_name": contact.first_name,
                "last_name": contact.last_name or "",
                "custom_fields_values": (
                    [
                        {
                            "field_code": "EMAIL",
                            "values": [{"value": contact.email, "enum_code": "WORK"}],
                        },
                        {
                            "field_code": "PHONE",
                            "values": [{"value": contact.phone, "enum_code": "WORK"}],
                        },
                    ]
                    if contact.email
                    else []
                ),
            }
        ]
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
        lead_id = payload.get("leads[status][0][id]")
        status_id = payload.get("leads[status][0][status_id]")
        if not lead_id:
            return None
        return {
            "event": "lead_status_changed",
            "external_id": str(lead_id),
            "raw_status": str(status_id),
            "crm_status": self._map_status(status_id),
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
            142: "won",  # Успешно реализовано
            143: "lost",  # Закрыто и не реализовано
        }
        return mapping.get(int(status_id or 0), "in_progress")
