from typing import Any, Dict, Optional

import structlog

from src.sync.audit_log import AuditLogger
from src.webhooks.verifier import WebhookVerifier

log = structlog.get_logger()


class WebhookHandler:
    """
    Обработчик вебхуков для различных CRM.
    """

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger

    async def handle_webhook(
        self,
        crm_type: str,
        headers: Dict[str, str],
        body: bytes,
        client_secret: str,
        webhook_secret: str = "",
    ) -> Dict[str, Any]:
        """
        Обрабатывает входящий вебхук от CRM.

        Returns:
            dict с результатом обработки
        """
        # Верифицируем подпись
        is_valid = WebhookVerifier.verify_webhook(
            crm_type, headers, body, client_secret, webhook_secret
        )

        if not is_valid:
            self.audit_logger.log_webhook_event(
                crm_type,
                "invalid_signature",
                "",
                "failure",
                error="Invalid webhook signature",
            )
            return {"status": "error", "message": "Invalid signature"}

        # Парсим тело вебхука
        try:
            import json

            payload = json.loads(body.decode("utf-8"))
        except Exception as e:
            self.audit_logger.log_webhook_event(
                crm_type,
                "parse_error",
                "",
                "failure",
                error=f"Failed to parse webhook body: {str(e)}",
            )
            return {"status": "error", "message": "Failed to parse payload"}

        # Определяем тип CRM и вызываем соответствующий обработчик
        if crm_type == "amocrm":
            result = await self._handle_amocrm_webhook(payload)
        elif crm_type == "bitrix24":
            result = await self._handle_bitrix24_webhook(payload)
        elif crm_type == "megaplan":
            result = await self._handle_megaplan_webhook(payload)
        elif crm_type == "salesforce":
            result = await self._handle_salesforce_webhook(payload)
        elif crm_type == "hubspot":
            result = await self._handle_hubspot_webhook(payload)
        elif crm_type == "pipedrive":
            result = await self._handle_pipedrive_webhook(payload)
        else:
            self.audit_logger.log_webhook_event(
                crm_type, "unknown_crm", "", "failure", error="Unknown CRM type"
            )
            return {"status": "error", "message": "Unknown CRM type"}

        return result

    async def _handle_amocrm_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка вебхука от amoCRM."""
        event_data = self._parse_amocrm_event(payload)
        if not event_data:
            self.audit_logger.log_webhook_event(
                "amocrm", "invalid_event", "", "failure", error="Invalid amoCRM event"
            )
            return {"status": "error", "message": "Invalid event data"}

        # Логируем событие
        self.audit_logger.log_webhook_event(
            "amocrm", event_data["event"], event_data["external_id"], "success"
        )

        # В реальной реализации здесь был бы вызов сервиса синхронизации
        # Для упрощения возвращаем успех
        return {"status": "success", "event": event_data}

    async def _handle_bitrix24_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка вебхука от Битрикс24."""
        event_data = self._parse_bitrix24_event(payload)
        if not event_data:
            self.audit_logger.log_webhook_event(
                "bitrix24",
                "invalid_event",
                "",
                "failure",
                error="Invalid Bitrix24 event",
            )
            return {"status": "error", "message": "Invalid event data"}

        self.audit_logger.log_webhook_event(
            "bitrix24", event_data["event"], event_data["external_id"], "success"
        )

        return {"status": "success", "event": event_data}

    async def _handle_megaplan_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка вебхука от Мегаплан."""
        event_data = self._parse_megaplan_event(payload)
        if not event_data:
            self.audit_logger.log_webhook_event(
                "megaplan",
                "invalid_event",
                "",
                "failure",
                error="Invalid Megaplan event",
            )
            return {"status": "error", "message": "Invalid event data"}

        self.audit_logger.log_webhook_event(
            "megaplan", event_data["event"], event_data["external_id"], "success"
        )

        return {"status": "success", "event": event_data}

    async def _handle_salesforce_webhook(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обработка вебхука от Salesforce."""
        event_data = self._parse_salesforce_event(payload)
        if not event_data:
            self.audit_logger.log_webhook_event(
                "salesforce",
                "invalid_event",
                "",
                "failure",
                error="Invalid Salesforce event",
            )
            return {"status": "error", "message": "Invalid event data"}

        self.audit_logger.log_webhook_event(
            "salesforce", event_data["event"], event_data["external_id"], "success"
        )

        return {"status": "success", "event": event_data}

    async def _handle_hubspot_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка вебхука от HubSpot."""
        event_data = self._parse_hubspot_event(payload)
        if not event_data:
            self.audit_logger.log_webhook_event(
                "hubspot", "invalid_event", "", "failure", error="Invalid HubSpot event"
            )
            return {"status": "error", "message": "Invalid event data"}

        self.audit_logger.log_webhook_event(
            "hubspot", event_data["event"], event_data["external_id"], "success"
        )

        return {"status": "success", "event": event_data}

    async def _handle_pipedrive_webhook(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обработка вебхука от Pipedrive."""
        event_data = self._parse_pipedrive_event(payload)
        if not event_data:
            self.audit_logger.log_webhook_event(
                "pipedrive",
                "invalid_event",
                "",
                "failure",
                error="Invalid Pipedrive event",
            )
            return {"status": "error", "message": "Invalid event data"}

        self.audit_logger.log_webhook_event(
            "pipedrive", event_data["event"], event_data["external_id"], "success"
        )

        return {"status": "success", "event": event_data}

    def _parse_amocrm_event(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Парсинг события amoCRM."""
        lead_id = payload.get("leads[status][0][id]")
        status_id = payload.get("leads[status][0][status_id]")
        if not lead_id:
            return None

        return {
            "event": "lead_status_changed",
            "external_id": str(lead_id),
            "raw_status": str(status_id),
            "crm_status": self._map_amocrm_status(status_id),
        }

    def _parse_bitrix24_event(
        self, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Парсинг события Битрикс24."""
        event = payload.get("event")
        if event and event in ("ONCRMLEAD_STATUS", "ONCRMLEAD_UPDATE"):
            data = payload.get("data", {})
            lead_id = data.get("FIELDS", {}).get("ID")
            status_id = data.get("FIELDS", {}).get("STATUS_ID")
            if lead_id:
                return {
                    "event": "lead_status_changed",
                    "external_id": str(lead_id),
                    "raw_status": str(status_id),
                    "crm_status": self._map_bitrix24_status(status_id),
                }
        return None

    def _parse_megaplan_event(
        self, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Парсинг события Мегаплан."""
        event_type = payload.get("eventType")
        if event_type == "lead.updated":
            lead_id = payload.get("leadId")
            if lead_id:
                return {
                    "event": "lead_status_changed",
                    "external_id": str(lead_id),
                    "raw_status": payload.get("status"),
                    "crm_status": payload.get("status"),
                }
        return None

    def _parse_salesforce_event(
        self, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Парсинг события Salesforce."""
        event_type = payload.get("event", {}).get("type")
        if event_type == "lead.updated":
            lead_id = payload.get("sobject", {}).get("Id")
            if lead_id:
                return {
                    "event": "lead_status_changed",
                    "external_id": str(lead_id),
                    "raw_status": payload.get("sobject", {}).get("Status"),
                    "crm_status": payload.get("sobject", {}).get("Status"),
                }
        return None

    def _parse_hubspot_event(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Парсинг события HubSpot."""
        event_type = payload.get("event", {}).get("type")
        if event_type == "contact.propertyChange":
            contact_id = payload.get("objectId")
            if contact_id:
                return {
                    "event": "lead_status_changed",
                    "external_id": str(contact_id),
                    "raw_status": payload.get("propertyName"),
                    "crm_status": payload.get("propertyName"),
                }
        return None

    def _parse_pipedrive_event(
        self, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Парсинг события Pipedrive."""
        event_type = payload.get("event_type")
        if event_type == "deal.updated":
            deal_id = payload.get("current", {}).get("id")
            if deal_id:
                return {
                    "event": "lead_status_changed",
                    "external_id": str(deal_id),
                    "raw_status": payload.get("current", {}).get("status"),
                    "crm_status": payload.get("current", {}).get("status"),
                }
        return None

    @staticmethod
    def _map_amocrm_status(status_id) -> str:
        mapping = {
            142: "won",
            143: "lost",
        }
        return mapping.get(int(status_id or 0), "in_progress")

    @staticmethod
    def _map_bitrix24_status(status_id) -> str:
        mapping = {
            "WON": "won",
            "LOST": "lost",
            "NEW": "new",
            "IN_PROGRESS": "in_progress",
        }
        return mapping.get(str(status_id), "in_progress")
