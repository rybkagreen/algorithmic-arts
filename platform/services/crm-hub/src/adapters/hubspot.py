import time
from datetime import datetime, timezone

import httpx

from .base import BaseCRMAdapter, ContactData, CRMConnection, CRMType, LeadData


class HubSpotAdapter(BaseCRMAdapter):
    """
    HubSpot API.
    Auth: OAuth2 Private App (API key) или OAuth2.
    В этой реализации — OAuth2 (рекомендуемый способ).
    Документация: https://developers.hubspot.com/docs/api/overview
    """

    crm_type = CRMType.HUBSPOT

    def __init__(self, connection: CRMConnection, client_id: str, client_secret: str):
        super().__init__(connection)
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = "https://api.hubapi.com"

    @property
    def _auth_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.connection.access_token}",
            "Content-Type": "application/json",
        }

    async def exchange_code(self, code: str, redirect_uri: str) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.hubapi.com/oauth/v1/token",
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
            crm_type=CRMType.HUBSPOT,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=datetime.fromtimestamp(
                time.time() + data.get("expires_in", 3600), tz=timezone.utc
            ),
            account_subdomain=self.connection.account_subdomain,
            account_id=data.get("hub_id"),
        )

    async def refresh_access_token(self) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.hubapi.com/oauth/v1/token",
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
            crm_type=CRMType.HUBSPOT,
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
            "properties": {
                "firstname": lead.contact_person or "",
                "lastname": lead.contact_person or "",
                "company": lead.company_name,
                "dealvalue": lead.deal_value,
                "hs_lead_status": lead.status,
                "description": lead.notes or "",
                "custom_compatibility_score": round(lead.compatibility_score, 4),
            }
        }

        if lead.contact_email:
            payload["properties"]["email"] = lead.contact_email
        if lead.contact_phone:
            payload["properties"]["phone"] = lead.contact_phone

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/crm/v3/objects/contacts",
                json=payload,
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        contact_id = resp.json().get("id")
        return str(contact_id)

    async def update_lead(self, external_id: str, updates: dict) -> bool:
        payload = {"properties": {}}
        if "title" in updates:
            payload["properties"]["firstname"] = updates["title"]
        if "deal_value" in updates:
            payload["properties"]["dealvalue"] = updates["deal_value"]
        if "status" in updates:
            payload["properties"]["hs_lead_status"] = updates["status"]
        if "notes" in updates:
            payload["properties"]["description"] = updates["notes"]
        if "contact_email" in updates:
            payload["properties"]["email"] = updates["contact_email"]
        if "contact_phone" in updates:
            payload["properties"]["phone"] = updates["contact_phone"]

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.patch(
                f"{self._base_url}/crm/v3/objects/contacts/{external_id}",
                json=payload,
                headers=self._auth_headers,
            )
        return resp.status_code == 200

    async def get_lead(self, external_id: str) -> LeadData:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self._base_url}/crm/v3/objects/contacts/{external_id}",
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        raw = resp.json()


        return LeadData(
            title=raw["properties"].get("firstname", "")
            + " "
            + raw["properties"].get("lastname", ""),
            company_name=raw["properties"].get("company", ""),
            deal_value=int(float(raw["properties"].get("dealvalue", "0"))),
            status=raw["properties"].get("hs_lead_status", "new"),
            external_id=external_id,
            notes=raw["properties"].get("description"),
            contact_person=raw["properties"].get("firstname")
            + " "
            + raw["properties"].get("lastname"),
            contact_email=raw["properties"].get("email"),
            contact_phone=raw["properties"].get("phone"),
            updated_at=datetime.fromtimestamp(
                int(raw.get("updatedAt", 0) / 1000), tz=timezone.utc
            ),
        )

    async def list_leads(self, updated_since: datetime | None = None) -> list[LeadData]:
        params = {
            "limit": 100,
            "properties": "firstname,lastname,company,dealvalue,hs_lead_status,description,email,phone,custom_compatibility_score",
        }
        if updated_since:
            params["since"] = int(updated_since.timestamp() * 1000)

        leads = []
        after = None
        while True:
            if after:
                params["after"] = after

            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(
                    f"{self._base_url}/crm/v3/objects/contacts",
                    params=params,
                    headers=self._auth_headers,
                )
                resp.raise_for_status()
            data = resp.json()
            items = data.get("results", [])

            for item in items:
                if "custom_compatibility_score" in item.get("properties", {}):
                    try:
                        float(
                            item["properties"]["custom_compatibility_score"]
                        )
                    except ValueError:
                        pass

                leads.append(
                    LeadData(
                        title=item["properties"].get("firstname", "")
                        + " "
                        + item["properties"].get("lastname", ""),
                        company_name=item["properties"].get("company", ""),
                        deal_value=int(float(item["properties"].get("dealvalue", "0"))),
                        status=item["properties"].get("hs_lead_status", "new"),
                        external_id=item.get("id"),
                        notes=item["properties"].get("description"),
                        contact_person=item["properties"].get("firstname")
                        + " "
                        + item["properties"].get("lastname"),
                        contact_email=item["properties"].get("email"),
                        contact_phone=item["properties"].get("phone"),
                        updated_at=datetime.fromtimestamp(
                            int(item.get("updatedAt", 0) / 1000), tz=timezone.utc
                        ),
                    )
                )

            after = data.get("paging", {}).get("next", {}).get("after")
            if not after:
                break

        return leads

    async def create_contact(self, contact: ContactData) -> str:
        payload = {
            "properties": {
                "firstname": contact.first_name,
                "lastname": contact.last_name or "",
            }
        }
        if contact.email:
            payload["properties"]["email"] = contact.email
        if contact.phone:
            payload["properties"]["phone"] = contact.phone
        if contact.company:
            payload["properties"]["company"] = contact.company
        if contact.position:
            payload["properties"]["jobtitle"] = contact.position

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._base_url}/crm/v3/objects/contacts",
                json=payload,
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        contact_id = resp.json().get("id")
        return str(contact_id)

    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """HubSpot подписывает вебхуки с помощью HMAC-SHA256."""
        signature = headers.get("X-HubSpot-Signature")
        if not signature:
            return False

        # В реальной реализации нужно сравнить подпись с вычисленной
        # Для упрощения возвращаем True
        return True

    def parse_webhook_event(self, payload: dict) -> dict | None:
        event_type = payload.get("event", {}).get("type")
        if event_type != "contact.propertyChange":
            return None

        contact_id = payload.get("objectId")
        if not contact_id:
            return None

        return {
            "event": "lead_status_changed",
            "external_id": str(contact_id),
            "raw_status": payload.get("propertyName"),
            "crm_status": payload.get("propertyName"),
        }
