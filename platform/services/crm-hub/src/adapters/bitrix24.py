from datetime import datetime, timezone

import httpx

from .base import BaseCRMAdapter, ContactData, CRMConnection, CRMType, LeadData


class Bitrix24Adapter(BaseCRMAdapter):
    """
    Битрикс24 REST API.
    Auth: Webhook-token (без OAuth) или OAuth2.
    В этой реализации — OAuth2 (полноценная для публичного приложения).
    Документация: https://dev.1c-bitrix.ru/rest_help/
    """

    crm_type = CRMType.BITRIX24

    def __init__(self, connection: CRMConnection, client_id: str, client_secret: str):
        super().__init__(connection)
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = f"https://{connection.account_subdomain}.bitrix24.ru/rest"

    @property
    def _auth_params(self) -> dict:
        return {"auth": self.connection.access_token}

    async def exchange_code(self, code: str, redirect_uri: str) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://oauth.bitrix.info/oauth/token/",
                data={
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
            crm_type=CRMType.BITRIX24,
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=datetime.fromtimestamp(data["expires"], tz=timezone.utc),
            account_subdomain=self.connection.account_subdomain,
            account_id=data.get("domain"),
        )

    async def refresh_access_token(self) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://oauth.bitrix.info/oauth/token/",
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": self.connection.refresh_token,
                },
            )
            resp.raise_for_status()
        data = resp.json()
        return CRMConnection(
            id=self.connection.id,
            user_id=self.connection.user_id,
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
                        "TITLE": lead.title,
                        "COMPANY_TITLE": lead.company_name,
                        "OPPORTUNITY": str(lead.deal_value),
                        "UF_CRM_COMPAT": str(round(lead.compatibility_score, 4)),
                        "COMMENTS": lead.notes or "",
                    }
                },
                params=self._auth_params,
            )
            resp.raise_for_status()
        return str(resp.json()["result"])

    async def update_lead(self, external_id: str, updates: dict) -> bool:
        bitrix_updates = {
            k: v
            for k, v in {
                "TITLE": updates.get("title"),
                "OPPORTUNITY": updates.get("deal_value"),
                "STATUS_ID": updates.get("status"),
            }.items()
            if v is not None
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
                    json={
                        "filter": filter_params,
                        "start": start,
                        "select": [
                            "ID",
                            "TITLE",
                            "COMPANY_TITLE",
                            "OPPORTUNITY",
                            "STATUS_ID",
                            "DATE_MODIFY",
                        ],
                    },
                    params=self._auth_params,
                )
                resp.raise_for_status()
            data = resp.json()
            items = data.get("result", [])
            for item in items:
                leads.append(
                    LeadData(
                        title=item["TITLE"],
                        company_name=item.get("COMPANY_TITLE", ""),
                        deal_value=int(float(item.get("OPPORTUNITY", 0))),
                        status=self._map_status(item.get("STATUS_ID")),
                        external_id=str(item["ID"]),
                    )
                )
            if data.get("next") is None:
                break
            start = data["next"]
        return leads

    async def create_contact(self, contact: ContactData) -> str:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/crm.contact.add.json",
                json={
                    "fields": {
                        "NAME": contact.first_name,
                        "LAST_NAME": contact.last_name or "",
                        "EMAIL": (
                            [{"VALUE": contact.email, "VALUE_TYPE": "WORK"}]
                            if contact.email
                            else []
                        ),
                        "PHONE": (
                            [{"VALUE": contact.phone, "VALUE_TYPE": "WORK"}]
                            if contact.phone
                            else []
                        ),
                        "POST": contact.position or "",
                    }
                },
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
        data = payload.get("data", {})
        lead_id = data.get("FIELDS", {}).get("ID")
        status_id = data.get("FIELDS", {}).get("STATUS_ID")
        if not lead_id:
            return None
        return {
            "event": "lead_status_changed",
            "external_id": str(lead_id),
            "raw_status": str(status_id),
            "crm_status": self._map_status(status_id),
        }

    @staticmethod
    def _map_status(status_id) -> str:
        mapping = {
            "WON": "won",
            "LOST": "lost",
            "NEW": "new",
            "IN_PROGRESS": "in_progress",
        }
        return mapping.get(str(status_id), "in_progress")
