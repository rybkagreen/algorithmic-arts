import time
from datetime import datetime, timezone

import httpx

from .base import BaseCRMAdapter, ContactData, CRMConnection, CRMType, LeadData


class MegaplanAdapter(BaseCRMAdapter):
    """
    Мегаплан API.
    Auth: Basic Auth (login:password) или OAuth2.
    В этой реализации — OAuth2 (рекомендуемый способ).
    Документация: https://wiki.megaplan.ru/API
    """

    crm_type = CRMType.MEGAPLAN

    def __init__(self, connection: CRMConnection, client_id: str, client_secret: str):
        super().__init__(connection)
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = f"https://{connection.account_subdomain}.megaplan.ru/api/v1"

    @property
    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.connection.access_token}"}

    async def exchange_code(self, code: str, redirect_uri: str) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/oauth/token",
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
            crm_type=CRMType.MEGAPLAN,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=datetime.fromtimestamp(
                time.time() + data.get("expires_in", 3600), tz=timezone.utc
            ),
            account_subdomain=self.connection.account_subdomain,
            account_id=data.get("account_id"),
        )

    async def refresh_access_token(self) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/oauth/token",
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
            crm_type=CRMType.MEGAPLAN,
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
            "name": lead.title,
            "companyName": lead.company_name,
            "price": lead.deal_value,
            "status": "new",
            "customFields": [
                {
                    "id": "compatibility_score",
                    "value": str(round(lead.compatibility_score, 4)),
                }
            ],
        }
        if lead.notes:
            payload["description"] = lead.notes
        if lead.contact_person:
            payload["contactPerson"] = lead.contact_person
        if lead.contact_email:
            payload["email"] = lead.contact_email
        if lead.contact_phone:
            payload["phone"] = lead.contact_phone

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/leads",
                json=payload,
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        lead_id = resp.json().get("id")
        return str(lead_id)

    async def update_lead(self, external_id: str, updates: dict) -> bool:
        payload = {}
        if "title" in updates:
            payload["name"] = updates["title"]
        if "deal_value" in updates:
            payload["price"] = updates["deal_value"]
        if "status" in updates:
            payload["status"] = updates["status"]
        if "notes" in updates:
            payload["description"] = updates["notes"]

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.patch(
                f"{self._base_url}/leads/{external_id}",
                json=payload,
                headers=self._auth_headers,
            )
        return resp.status_code == 200

    async def get_lead(self, external_id: str) -> LeadData:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self._base_url}/leads/{external_id}",
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        raw = resp.json()

        return LeadData(
            title=raw.get("name", ""),
            company_name=raw.get("companyName", ""),
            deal_value=raw.get("price", 0),
            status=raw.get("status", "new"),
            external_id=external_id,
            notes=raw.get("description"),
            contact_person=raw.get("contactPerson"),
            contact_email=raw.get("email"),
            contact_phone=raw.get("phone"),
            updated_at=datetime.fromtimestamp(raw.get("updatedAt", 0), tz=timezone.utc),
        )

    async def list_leads(self, updated_since: datetime | None = None) -> list[LeadData]:
        params = {"limit": 100}
        if updated_since:
            params["updatedSince"] = int(updated_since.timestamp())

        leads = []
        page = 1
        while True:
            params["page"] = page
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(
                    f"{self._base_url}/leads",
                    params=params,
                    headers=self._auth_headers,
                )
                resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            if not items:
                break

            for item in items:
                for cf in item.get("customFields", []):
                    if cf.get("id") == "compatibility_score":
                        try:
                            float(cf.get("value", "0"))
                        except ValueError:
                            pass

                leads.append(
                    LeadData(
                        title=item.get("name", ""),
                        company_name=item.get("companyName", ""),
                        deal_value=item.get("price", 0),
                        status=item.get("status", "new"),
                        external_id=str(item.get("id")),
                        notes=item.get("description"),
                        contact_person=item.get("contactPerson"),
                        contact_email=item.get("email"),
                        contact_phone=item.get("phone"),
                        updated_at=datetime.fromtimestamp(
                            item.get("updatedAt", 0), tz=timezone.utc
                        ),
                    )
                )

            if len(items) < 100:
                break
            page += 1

        return leads

    async def create_contact(self, contact: ContactData) -> str:
        payload = {
            "firstName": contact.first_name,
            "lastName": contact.last_name or "",
        }
        if contact.email:
            payload["email"] = contact.email
        if contact.phone:
            payload["phone"] = contact.phone
        if contact.company:
            payload["company"] = contact.company
        if contact.position:
            payload["position"] = contact.position

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/contacts",
                json=payload,
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        contact_id = resp.json().get("id")
        return str(contact_id)

    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """Мегаплан не подписывает вебхуки по умолчанию."""
        return True

    def parse_webhook_event(self, payload: dict) -> dict | None:
        event_type = payload.get("eventType")
        if event_type != "lead.updated":
            return None

        lead_id = payload.get("leadId")
        if not lead_id:
            return None

        return {
            "event": "lead_status_changed",
            "external_id": str(lead_id),
            "raw_status": payload.get("status"),
            "crm_status": payload.get("status"),
        }
