
import structlog
from fastapi import APIRouter, HTTPException, Request

from ..sync.audit_log import AuditLogger
from .handlers import WebhookHandler

log = structlog.get_logger()

router = APIRouter(prefix="/crm/webhooks", tags=["webhooks"])

# Создаем экземпляр обработчика вебхуков
audit_logger = AuditLogger()
webhook_handler = WebhookHandler(audit_logger)


@router.post("/{crm_type}")
async def handle_webhook(
    crm_type: str,
    request: Request,
    # В реальной реализации здесь будут зависимости для получения client_secret и webhook_secret
    # Для упрощения используем заглушки
):
    """
    Обработчик вебхуков от CRM систем.

    Параметры:
        crm_type: тип CRM (amocrm, bitrix24, megaplan, salesforce, hubspot, pipedrive)
    """
    # Получаем заголовки и тело запроса
    headers = dict(request.headers)
    body = await request.body()

    # В реальной реализации client_secret и webhook_secret должны быть получены из конфигурации или базы данных
    # Для упрощения используем заглушки
    client_secret = "dummy_client_secret"
    webhook_secret = "dummy_webhook_secret"

    try:
        result = await webhook_handler.handle_webhook(
            crm_type, headers, body, client_secret, webhook_secret
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Webhook processing failed"),
            )

        return result

    except Exception as e:
        log.error("webhook_error", crm_type=crm_type, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
