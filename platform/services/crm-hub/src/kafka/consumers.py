import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID

import structlog
from aiokafka import AIOKafkaConsumer

from src.adapters.base import CRMConnection, CRMType
from src.sync.audit_log import AuditLogger
from src.sync.conflict_resolver import ConflictResolutionStrategy
from src.sync.field_mapper import FieldMapper
from src.sync.sync_service import SyncService

log = structlog.get_logger()


class CRMKafkaConsumer:
    """
    Потребитель Kafka для обработки запросов на синхронизацию.
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self.running = False

    async def start(self):
        """Запускает потребитель Kafka."""
        self.consumer = AIOKafkaConsumer(
            "crm.sync.requested",
            bootstrap_servers=self.bootstrap_servers,
            group_id="crm-hub-consumer-group",
            auto_offset_reset="latest",
            enable_auto_commit=True,
        )
        await self.consumer.start()
        self.running = True
        log.info("kafka_consumer_started", topic="crm.sync.requested")

    async def stop(self):
        """Останавливает потребитель Kafka."""
        if self.consumer:
            await self.consumer.stop()
        self.running = False
        log.info("kafka_consumer_stopped")

    async def consume_messages(self):
        """Основной цикл потребления сообщений."""
        if not self.consumer:
            raise RuntimeError("Consumer not started")

        try:
            async for msg in self.consumer:
                try:
                    # Декодируем сообщение
                    message = json.loads(msg.value.decode("utf-8"))
                    await self._handle_message(message)
                except Exception as e:
                    log.error("kafka_message_error", error=str(e), message=msg.value)
        except Exception as e:
            log.error("kafka_consumer_error", error=str(e))

    async def _handle_message(self, message: Dict[str, Any]):
        """Обрабатывает одно сообщение из Kafka."""
        event_type = message.get("event_type")

        if event_type == "sync_request":
            await self._handle_sync_request(message)
        elif event_type == "token_refresh_request":
            await self._handle_token_refresh_request(message)
        else:
            log.warning("unknown_kafka_event", event_type=event_type)

    async def _handle_sync_request(self, message: Dict[str, Any]):
        """Обрабатывает запрос на синхронизацию."""
        connection_id_str = message.get("connection_id")
        if not connection_id_str:
            log.error("sync_request_missing_connection_id")
            return

        try:
            connection_id = UUID(connection_id_str)

            # В реальной реализации здесь будет получение подключения из БД
            # Для упрощения используем заглушку

            CRMConnection(
                id=connection_id,
                user_id=UUID("00000000-0000-0000-0000-000000000000"),
                crm_type=CRMType.AMOCRM,
                access_token="dummy_access_token",
                refresh_token="dummy_refresh_token",
                expires_at=datetime.now(timezone.utc),
                account_subdomain="example",
                account_id="12345",
            )

            # Создаем адаптер и сервис синхронизации
            adapter = None  # В реальной реализации здесь будет создание адаптера
            sync_service = SyncService(
                adapter=adapter,
                field_mapper=FieldMapper(),
                conflict_resolver=ConflictResolutionStrategy(),
                audit_logger=AuditLogger(),
            )

            # Выполняем синхронизацию
            leads = await sync_service.from_crm(connection_id)

            log.info(
                "sync_request_processed",
                connection_id=str(connection_id),
                leads_synced=len(leads),
            )

        except Exception as e:
            log.error(
                "sync_request_error", error=str(e), connection_id=connection_id_str
            )

    async def _handle_token_refresh_request(self, message: Dict[str, Any]):
        """Обрабатывает запрос на обновление токена."""
        connection_id_str = message.get("connection_id")
        if not connection_id_str:
            log.error("token_refresh_request_missing_connection_id")
            return

        try:
            connection_id = UUID(connection_id_str)

            # В реальной реализации здесь будет получение подключения из БД
            # Для упрощения используем заглушку

            CRMConnection(
                id=connection_id,
                user_id=UUID("00000000-0000-0000-0000-000000000000"),
                crm_type=CRMType.AMOCRM,
                access_token="dummy_access_token",
                refresh_token="dummy_refresh_token",
                expires_at=datetime.now(timezone.utc),
                account_subdomain="example",
                account_id="12345",
            )

            # Создаем адаптер
            adapter = None  # В реальной реализации здесь будет создание адаптера

            # Обновляем токен
            await adapter.refresh_access_token()

            log.info(
                "token_refresh_request_processed", connection_id=str(connection_id)
            )

        except Exception as e:
            log.error(
                "token_refresh_request_error",
                error=str(e),
                connection_id=connection_id_str,
            )


# Глобальный экземпляр потребителя
consumer = CRMKafkaConsumer()


async def start_kafka_consumer():
    """Функция для запуска потребителя Kafka."""
    await consumer.start()
    asyncio.create_task(consumer.consume_messages())
