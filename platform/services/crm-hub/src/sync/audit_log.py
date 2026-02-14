from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import structlog

log = structlog.get_logger()


class AuditLogger:
    """
    Аудит лог для всех операций синхронизации.
    """

    def __init__(self):
        pass

    def log_sync_event(
        self,
        event_type: str,
        connection_id: UUID,
        external_id: Optional[str],
        description: str,
        status: str,
        error: Optional[str] = None,
    ):
        """
        Логирует событие синхронизации.
        """
        log.info(
            "crm_sync_event",
            event_type=event_type,
            connection_id=str(connection_id),
            external_id=external_id,
            description=description,
            status=status,
            error=error,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def log_token_operation(
        self,
        operation: str,
        connection_id: UUID,
        status: str,
        error: Optional[str] = None,
    ):
        """
        Логирует операции с токенами.
        """
        log.info(
            "crm_token_operation",
            operation=operation,
            connection_id=str(connection_id),
            status=status,
            error=error,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def log_webhook_event(
        self,
        crm_type: str,
        event_type: str,
        external_id: str,
        status: str,
        error: Optional[str] = None,
    ):
        """
        Логирует события вебхуков.
        """
        log.info(
            "crm_webhook_event",
            crm_type=crm_type,
            event_type=event_type,
            external_id=external_id,
            status=status,
            error=error,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
