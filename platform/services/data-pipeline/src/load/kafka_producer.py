import json
import structlog
from aiokafka import AIOKafkaProducer
from typing import Dict, Any

log = structlog.get_logger()

class KafkaProducer:
    def __init__(self, bootstrap_servers: str = "kafka:9092"):
        self.bootstrap_servers = bootstrap_servers
        self._producer = None

    async def start(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._producer.start()

    async def stop(self):
        if self._producer:
            await self._producer.stop()
            self._producer = None

    async def publish_company_raw(self, company_data: Dict[str, Any]):
        """Публикует сырые данные компании в топик company.raw_data."""
        try:
            if not self._producer:
                await self.start()
            
            await self._producer.send_and_wait(
                "company.raw_data",
                value=company_data,
                key=str(company_data.get("name", "")).encode("utf-8")
            )
            log.info("company_raw_published", name=company_data.get("name"))
        except Exception as exc:
            log.error("kafka_publish_failed", error=str(exc), company_name=company_data.get("name"))
            raise

    async def publish_company_created(self, company_id: str, company_data: Dict[str, Any]):
        """Публикует событие company.created после успешного upsert."""
        try:
            if not self._producer:
                await self.start()
            
            event = {
                "company_id": company_id,
                "name": company_data.get("name"),
                "source": company_data.get("source"),
                "created_at": company_data.get("created_at"),
            }
            await self._producer.send_and_wait(
                "company.created",
                value=event,
                key=company_id.encode("utf-8")
            )
            log.info("company_created_published", company_id=company_id)
        except Exception as exc:
            log.error("company_created_publish_failed", error=str(exc), company_id=company_id)
            raise