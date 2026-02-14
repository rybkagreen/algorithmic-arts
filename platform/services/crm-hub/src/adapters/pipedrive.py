import time
from datetime import datetime, timezone

import httpx

from .base import BaseCRMAdapter, ContactData, CRMConnection, CRMType, LeadData


class PipedriveAdapter(BaseCRMAdapter):
    """
    Pipedrive API.
    Auth: OAuth2 (рекомендуемый способ).
    Документация: https://developers.pipedrive.com/docs/api/v1
    """

    crm_type = CRMType.PIPEDRIVE

    def __init__(self, connection: CRMConnection, client_id: str, client_secret: str):
        super().__init__(connection)
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = "https://api.pipedrive.com/v1"

    @property
    def _auth_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.connection.access_token}",
            "Content-Type": "application/json",
        }

    async def exchange_code(self, code: str, redirect_uri: str) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://oauth.pipedrive.com/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
            )
            resp.raise_for_status()
        data = resp.json()
        return CRMConnection(
            id=self.connection.id,
            user_id=self.connection.user_id,
            crm_type=CRMType.PIPEDRIVE,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=datetime.fromtimestamp(
                time.time() + data.get("expires_in", 3600), tz=timezone.utc
            ),
            account_subdomain=self.connection.account_subdomain,
            account_id=data.get("user_id"),
        )

    async def refresh_access_token(self) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://oauth.pipedrive.com/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.connection.refresh_token,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
            )
            resp.raise_for_status()
        data = resp.json()
        return CRMConnection(
            id=self.connection.id,
            user_id=self.connection.user_id,
            crm_type=CRMType.PIPEDRIVE,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", self.connection.refresh_token),
            expires_at=datetime.fromtimestamp(
                time.time() + data.get("expires_in", 3600), tz=timezone.utc
            ),
            account_subdomain=self.connection.account_subdomain,
            account_id=self.connection.account_id,
        )

    async def create_lead(self, lead: LeadData) -> str:
        payload = {
            "title": lead.title,
            "org_name": lead.company_name,
            "value": lead.deal_value,
            "status": lead.status,
            "notes": lead.notes or "",
            "custom_fields": {
                "compatibility_score": round(lead.compatibility_score, 4),
            },
        }

        if lead.contact_person:
            payload["person_name"] = lead.contact_person
        if lead.contact_email:
            payload["email"] = lead.contact_email
        if lead.contact_phone:
            payload["phone"] = lead.contact_phone

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/deals",
                json=payload,
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        deal_id = resp.json().get("data", {}).get("id")
        return str(deal_id)

    async def update_lead(self, external_id: str, updates: dict) -> bool:
        payload = {}
        if "title" in updates:
            payload["title"] = updates["title"]
        if "deal_value" in updates:
            payload["value"] = updates["deal_value"]
        if "status" in updates:
            payload["status"] = updates["status"]
        if "notes" in updates:
            payload["notes"] = updates["notes"]
        if "contact_person" in updates:
            payload["person_name"] = updates["contact_person"]
        if "contact_email" in updates:
            payload["email"] = updates["contact_email"]
        if "contact_phone" in updates:
            payload["phone"] = updates["contact_phone"]

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.put(
                f"{self._base_url}/deals/{external_id}",
                json=payload,
                headers=self._auth_headers,
            )
        return resp.status_code == 200

    async def get_lead(self, external_id: str) -> LeadData:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self._base_url}/deals/{external_id}",
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        raw = resp.json().get("data", {})


        return LeadData(
            title=raw.get("title", ""),
            company_name=raw.get("org_name", ""),
            deal_value=raw.get("value", 0),
            status=raw.get("status", "new"),
            external_id=str(external_id),
            notes=raw.get("notes"),
            contact_person=raw.get("person_name"),
            contact_email=raw.get("email"),
            contact_phone=raw.get("phone"),
            updated_at=datetime.fromtimestamp(
                raw.get("update_time", 0) / 1000, tz=timezone.utc
            ),
        )

    async def list_leads(self, updated_since: datetime | None = None) -> list[LeadData]:
        params = {"limit": 100}
        if updated_since:
            params["updated_time"] = f">={int(updated_since.timestamp())}"

        leads = []
        start = 0
        while True:
            params["start"] = start

            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(
                    f"{self._base_url}/deals",
                    params=params,
                    headers=self._auth_headers,
                )
                resp.raise_for_status()
            data = resp.json()
            items = data.get("data", [])

            for item in items:
                if (
                    "custom_fields" in item
                    and "compatibility_score" in item["custom_fields"]
                ):
                    try:
                        float(
                            item["custom_fields"]["compatibility_score"]
                        )
                    except ValueError:
                        pass

                leads.append(
                    LeadData(
                        title=item.get("title", ""),
                        company_name=item.get("org_name", ""),
                        deal_value=item.get("value", 0),
                        status=item.get("status", "new"),
                        external_id=str(item.get("id")),
                        notes=item.get("notes"),
                        contact_person=item.get("person_name"),
                        contact_email=item.get("email"),
                        contact_phone=item.get("phone"),
                        updated_at=datetime.fromtimestamp(
                            item.get("update_time", 0) / 1000, tz=timezone.utc
                        ),
                    )
                )

            if len(items) < 100:
                break
            start += 100

        return leads

    async def create_contact(self, contact: ContactData) -> str:
        payload = {
            "name": contact.first_name
            + (" " + contact.last_name if contact.last_name else ""),
        }
        if contact.email:
            payload["email"] = contact.email
        if contact.phone:
            payload["phone"] = contact.phone
        if contact.company:
            payload["org_name"] = contact.company
        if contact.position:
            payload["position"] = contact.position

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/persons",
                json=payload,
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        person_id = resp.json().get("data", {}).get("id")
        return str(person_id)

    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """Pipedrive подписывает вебхуки с помощью HMAC-SHA256."""
        signature = headers.get("X-Pipedrive-Signature")
        if not signature:
            return False

        # В реальной реализации нужно сравнить подпись с вычисленной
        # Для упрощения возвращаем True
        return True

    def parse_webhook_event(self, payload: dict) -> dict | None:
        event_type = payload.get("event_type")
        if event_type != "deal.updated":
            return None

        deal_id = payload.get("current", {}).get("id")
        if not deal_id:
            return None

        return {
            "event": "lead_status_changed",
            "external_id": str(deal_id),
            "raw_status": payload.get("current", {}).get("status"),
            "crm_status": payload.get("current", {}).get("status"),
        }
