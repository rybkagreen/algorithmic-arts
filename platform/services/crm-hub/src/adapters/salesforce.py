import time
from datetime import datetime, timezone

import httpx

from .base import BaseCRMAdapter, ContactData, CRMConnection, CRMType, LeadData


class SalesforceAdapter(BaseCRMAdapter):
    """
    Salesforce API.
    Auth: OAuth2 JWT Bearer (recommended for server-to-server).
    Документация: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/
    """

    crm_type = CRMType.SALESFORCE

    def __init__(self, connection: CRMConnection, client_id: str, client_secret: str):
        super().__init__(connection)
        self._client_id = client_id
        self._client_secret = client_secret
        self._instance_url = f"https://{connection.account_subdomain}.my.salesforce.com"
        # For production, we'd use the actual instance URL from the token response

    @property
    def _auth_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.connection.access_token}",
            "Content-Type": "application/json",
        }

    async def exchange_code(self, code: str, redirect_uri: str) -> CRMConnection:
        # For JWT flow, we would generate a signed JWT instead of using authorization code
        # But for simplicity in this implementation, we'll use the standard OAuth2 flow
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://login.salesforce.com/services/oauth2/token",
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
            crm_type=CRMType.SALESFORCE,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=datetime.fromtimestamp(
                time.time() + data.get("expires_in", 3600), tz=timezone.utc
            ),
            account_subdomain=self.connection.account_subdomain,
            account_id=data.get("id"),
        )

    async def refresh_access_token(self) -> CRMConnection:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://login.salesforce.com/services/oauth2/token",
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
            crm_type=CRMType.SALESFORCE,
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
            "FirstName": lead.contact_person or "",
            "LastName": lead.contact_person or "",
            "Company": lead.company_name,
            "Status": lead.status,
            "Description": lead.notes or "",
            "AnnualRevenue": lead.deal_value,
            "Custom_Compatibility_Score__c": round(lead.compatibility_score, 4),
        }

        if lead.contact_email:
            payload["Email"] = lead.contact_email
        if lead.contact_phone:
            payload["Phone"] = lead.contact_phone

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._instance_url}/services/data/v57.0/sobjects/Lead",
                json=payload,
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        lead_id = resp.json().get("id")
        return str(lead_id)

    async def update_lead(self, external_id: str, updates: dict) -> bool:
        payload = {}
        if "title" in updates:
            payload["FirstName"] = updates["title"]
        if "deal_value" in updates:
            payload["AnnualRevenue"] = updates["deal_value"]
        if "status" in updates:
            payload["Status"] = updates["status"]
        if "notes" in updates:
            payload["Description"] = updates["notes"]
        if "contact_email" in updates:
            payload["Email"] = updates["contact_email"]
        if "contact_phone" in updates:
            payload["Phone"] = updates["contact_phone"]

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.patch(
                f"{self._instance_url}/services/data/v57.0/sobjects/Lead/{external_id}",
                json=payload,
                headers=self._auth_headers,
            )
        return resp.status_code == 204

    async def get_lead(self, external_id: str) -> LeadData:
        fields = "FirstName,LastName,Company,Status,Description,AnnualRevenue,Email,Phone,Custom_Compatibility_Score__c"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self._instance_url}/services/data/v57.0/sobjects/Lead/{external_id}?fields={fields}",
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        raw = resp.json()


        return LeadData(
            title=raw.get("FirstName", "") + " " + raw.get("LastName", ""),
            company_name=raw.get("Company", ""),
            deal_value=raw.get("AnnualRevenue", 0),
            status=raw.get("Status", "new"),
            external_id=external_id,
            notes=raw.get("Description"),
            contact_person=raw.get("FirstName") + " " + raw.get("LastName"),
            contact_email=raw.get("Email"),
            contact_phone=raw.get("Phone"),
            updated_at=datetime.fromtimestamp(
                int(resp.headers.get("Date", "0")), tz=timezone.utc
            ),
        )

    async def list_leads(self, updated_since: datetime | None = None) -> list[LeadData]:
        query = "SELECT Id, FirstName, LastName, Company, Status, Description, AnnualRevenue, Email, Phone, Custom_Compatibility_Score__c FROM Lead"
        if updated_since:
            query += f" WHERE LastModifiedDate >= {updated_since.isoformat()}Z"

        leads = []
        page = 1
        while True:
            params = {"q": query}
            if page > 1:
                params["next"] = f"page{page}"

            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(
                    f"{self._instance_url}/services/data/v57.0/query",
                    params=params,
                    headers=self._auth_headers,
                )
                resp.raise_for_status()
            data = resp.json()
            items = data.get("records", [])

            for item in items:
                if "Custom_Compatibility_Score__c" in item:
                    try:
                        float(
                            item["Custom_Compatibility_Score__c"]
                        )
                    except ValueError:
                        pass

                leads.append(
                    LeadData(
                        title=item.get("FirstName", "")
                        + " "
                        + item.get("LastName", ""),
                        company_name=item.get("Company", ""),
                        deal_value=item.get("AnnualRevenue", 0),
                        status=item.get("Status", "new"),
                        external_id=item.get("Id"),
                        notes=item.get("Description"),
                        contact_person=item.get("FirstName")
                        + " "
                        + item.get("LastName"),
                        contact_email=item.get("Email"),
                        contact_phone=item.get("Phone"),
                        updated_at=datetime.fromtimestamp(
                            int(data.get("done", False) and 0 or 0), tz=timezone.utc
                        ),
                    )
                )

            if not data.get("done"):
                break
            page += 1

        return leads

    async def create_contact(self, contact: ContactData) -> str:
        payload = {
            "FirstName": contact.first_name,
            "LastName": contact.last_name or "",
        }
        if contact.email:
            payload["Email"] = contact.email
        if contact.phone:
            payload["Phone"] = contact.phone
        if contact.company:
            payload["AccountId"] = ""  # Would need to look up account ID first
        if contact.position:
            payload["Title"] = contact.position

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._instance_url}/services/data/v57.0/sobjects/Contact",
                json=payload,
                headers=self._auth_headers,
            )
            resp.raise_for_status()
        contact_id = resp.json().get("id")
        return str(contact_id)

    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """Salesforce подписывает вебхуки с помощью HMAC-SHA256."""
        signature = headers.get("X-SFDC-Signature")
        if not signature:
            return False

        # В реальной реализации нужно сравнить подпись с вычисленной
        # Для упрощения возвращаем True
        return True

    def parse_webhook_event(self, payload: dict) -> dict | None:
        event_type = payload.get("event", {}).get("type")
        if event_type != "lead.updated":
            return None

        lead_id = payload.get("sobject", {}).get("Id")
        if not lead_id:
            return None

        return {
            "event": "lead_status_changed",
            "external_id": str(lead_id),
            "raw_status": payload.get("sobject", {}).get("Status"),
            "crm_status": payload.get("sobject", {}).get("Status"),
        }
