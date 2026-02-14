import json
from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from aiokafka import AIOKafkaConsumer
from elasticsearch import AsyncElasticsearch
from shared.logging import get_logger
from ..config import settings
from ..domain.company import Company
from ..infrastructure.elasticsearch.company_indexer import CompanyIndexer

logger = get_logger("company-projection-worker")


class CompanyProjectionWorker:
    """Kafka consumer для обновления read models (Elasticsearch) из domain events."""

    def __init__(self, es_client: AsyncElasticsearch, indexer: CompanyIndexer):
        self.es_client = es_client
        self.indexer = indexer
        self.consumer = None

    async def start(self):
        """Запуск Kafka consumer для обработки company events."""
        self.consumer = AIOKafkaConsumer(
            "company.events",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="company-read-model-projection",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            enable_auto_commit=True,
            auto_offset_reset="earliest"
        )
        await self.consumer.start()
        logger.info("company_projection_worker_started", status="running")

    async def stop(self):
        """Остановка consumer."""
        if self.consumer:
            await self.consumer.stop()
            logger.info("company_projection_worker_stopped")

    async def handle_event(self, event_data: Dict[str, Any]) -> None:
        """Обработка отдельного domain event."""
        try:
            event_type = event_data.get("event_type")
            aggregate_id = event_data.get("aggregate_id")
            
            if not event_type or not aggregate_id:
                logger.warning("invalid_event_received", event_data=event_data)
                return

            # Обработка различных типов событий
            if event_type == "company.created":
                await self._handle_company_created(event_data)
            elif event_type == "company.updated":
                await self._handle_company_updated(event_data)
            elif event_type == "company.enriched":
                await self._handle_company_enriched(event_data)
            else:
                logger.debug("unknown_event_type", event_type=event_type)

        except Exception as e:
            logger.error("projection_worker_error", error=str(e), event_data=event_data)
            raise

    async def _handle_company_created(self, event_data: Dict[str, Any]) -> None:
        """Обработка события company.created - создание документа в Elasticsearch."""
        try:
            company_id = UUID(event_data["payload"]["company_id"])
            company_data = event_data["payload"]
            
            # Преобразуем в Company объект для индексации
            company = Company(
                id=company_id,
                name=company_data["name"],
                slug=company_data.get("slug", ""),
                description=company_data.get("description"),
                website=company_data.get("website"),
                industry=company_data.get("industry", ""),
                sub_industries=company_data.get("sub_industries", []),
                business_model=company_data.get("business_model"),
                founded_year=company_data.get("founded_year"),
                headquarters_country=company_data.get("headquarters_country", "RU"),
                headquarters_city=company_data.get("headquarters_city"),
                employees_count=company_data.get("employees_count"),
                employees_range=company_data.get("employees_range"),
                funding_total=None,  # Пока не реализовано
                funding_stage=company_data.get("funding_stage"),
                last_funding_date=None,
                inn=None,
                ogrn=None,
                legal_name=company_data.get("legal_name"),
                tech_stack=company_data.get("tech_stack", {}),
                integrations=company_data.get("integrations", []),
                api_available=company_data.get("api_available", False),
                ai_summary=company_data.get("ai_summary"),
                ai_tags=company_data.get("ai_tags", []),
                embedding=company_data.get("embedding"),
                is_verified=company_data.get("is_verified", False),
                view_count=0,
                created_at=datetime.fromisoformat(company_data["created_at"]),
                updated_at=datetime.fromisoformat(company_data["updated_at"]),
                deleted_at=None
            )

            # Индексируем в Elasticsearch
            await self.indexer.index_company(company)
            logger.info("company_created_indexed", company_id=str(company.id))

        except Exception as e:
            logger.error("handle_company_created_error", error=str(e), event_data=event_data)
            raise

    async def _handle_company_updated(self, event_data: Dict[str, Any]) -> None:
        """Обработка события company.updated - обновление документа в Elasticsearch."""
        try:
            company_id = UUID(event_data["payload"]["company_id"])
            changed_fields = event_data["payload"].get("changed_fields", [])
            company_data = event_data["payload"]
            
            # Получаем текущий документ из ES
            try:
                response = await self.es_client.get(
                    index="companies",
                    id=str(company_id)
                )
                current_doc = response["_source"]
            except Exception:
                # Если документ не существует, создаем его
                await self._handle_company_created(event_data)
                return

            # Обновляем только измененные поля
            for field in changed_fields:
                if field in company_data:
                    current_doc[field] = company_data[field]

            # Обновляем timestamp
            current_doc["updated_at"] = datetime.utcnow().isoformat()

            # Обновляем в Elasticsearch
            await self.es_client.update(
                index="companies",
                id=str(company_id),
                doc=current_doc
            )
            logger.info("company_updated_indexed", company_id=str(company_id), fields=changed_fields)

        except Exception as e:
            logger.error("handle_company_updated_error", error=str(e), event_data=event_data)
            raise

    async def _handle_company_enriched(self, event_data: Dict[str, Any]) -> None:
        """Обработка события company.enriched - обновление enriched данных в Elasticsearch."""
        try:
            company_id = UUID(event_data["payload"]["company_id"])
            enrichment_data = event_data["payload"]
            
            # Обновляем только enriched поля
            update_doc = {
                "doc": {
                    "ai_summary": enrichment_data.get("ai_summary"),
                    "ai_tags": enrichment_data.get("ai_tags", []),
                    "tech_stack": enrichment_data.get("tech_stack", {}),
                    "integrations": enrichment_data.get("integrations", []),
                    "embedding": enrichment_data.get("embedding"),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }

            await self.es_client.update(
                index="companies",
                id=str(company_id),
                body=update_doc
            )
            logger.info("company_enriched_indexed", company_id=str(company_id))

        except Exception as e:
            logger.error("handle_company_enriched_error", error=str(e), event_data=event_data)
            raise

    async def run(self):
        """Основной цикл обработки событий."""
        if not self.consumer:
            await self.start()

        try:
            async for msg in self.consumer:
                try:
                    event_data = msg.value
                    await self.handle_event(event_data)
                except Exception as e:
                    logger.error("event_processing_failed", 
                               event_id=msg.key, error=str(e))
                    # В реальном приложении здесь был бы dead-letter queue
        except Exception as e:
            logger.error("projection_worker_crashed", error=str(e))
            raise
        finally:
            await self.stop()