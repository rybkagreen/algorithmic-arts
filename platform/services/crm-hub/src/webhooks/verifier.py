import hashlib
import hmac
from typing import Dict


class WebhookVerifier:
    """
    Верификатор подписей вебхуков для различных CRM.
    """

    @staticmethod
    def verify_amocrm_webhook(headers: Dict[str, str], body: bytes) -> bool:
        """
        amoCRM не подписывает вебхуки по умолчанию.
        В продакшене следует использовать IP-белый список.
        """
        return True

    @staticmethod
    def verify_bitrix24_webhook(
        headers: Dict[str, str], body: bytes, client_secret: str
    ) -> bool:
        """
        Битрикс24 подписывает вебхуки с помощью client_secret.
        """
        signature = headers.get("X-Bitrix-Signature")
        if not signature:
            return False

        # Вычисляем подпись
        expected_signature = hmac.new(
            client_secret.encode(), body, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    def verify_megaplan_webhook(
        headers: Dict[str, str], body: bytes, webhook_secret: str
    ) -> bool:
        """
        Мегаплан подписывает вебхуки с помощью webhook_secret.
        """
        signature = headers.get("X-Megaplan-Signature")
        if not signature:
            return False

        # Вычисляем подпись
        expected_signature = hmac.new(
            webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    def verify_salesforce_webhook(
        headers: Dict[str, str], body: bytes, client_secret: str
    ) -> bool:
        """
        Salesforce подписывает вебхуки с помощью HMAC-SHA256.
        """
        signature = headers.get("X-SFDC-Signature")
        if not signature:
            return False

        # Вычисляем подпись
        expected_signature = hmac.new(
            client_secret.encode(), body, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    def verify_hubspot_webhook(
        headers: Dict[str, str], body: bytes, client_secret: str
    ) -> bool:
        """
        HubSpot подписывает вебхуки с помощью HMAC-SHA256.
        """
        signature = headers.get("X-HubSpot-Signature")
        if not signature:
            return False

        # Вычисляем подпись
        expected_signature = hmac.new(
            client_secret.encode(), body, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    def verify_pipedrive_webhook(
        headers: Dict[str, str], body: bytes, client_secret: str
    ) -> bool:
        """
        Pipedrive подписывает вебхуки с помощью HMAC-SHA256.
        """
        signature = headers.get("X-Pipedrive-Signature")
        if not signature:
            return False

        # Вычисляем подпись
        expected_signature = hmac.new(
            client_secret.encode(), body, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    def verify_webhook(
        crm_type: str,
        headers: Dict[str, str],
        body: bytes,
        client_secret: str,
        webhook_secret: str = "",
    ) -> bool:
        """
        Унифицированный метод верификации вебхуков.
        """
        if crm_type == "amocrm":
            return WebhookVerifier.verify_amocrm_webhook(headers, body)
        elif crm_type == "bitrix24":
            return WebhookVerifier.verify_bitrix24_webhook(headers, body, client_secret)
        elif crm_type == "megaplan":
            return WebhookVerifier.verify_megaplan_webhook(
                headers, body, webhook_secret or client_secret
            )
        elif crm_type == "salesforce":
            return WebhookVerifier.verify_salesforce_webhook(
                headers, body, client_secret
            )
        elif crm_type == "hubspot":
            return WebhookVerifier.verify_hubspot_webhook(headers, body, client_secret)
        elif crm_type == "pipedrive":
            return WebhookVerifier.verify_pipedrive_webhook(
                headers, body, client_secret
            )
        else:
            return False
