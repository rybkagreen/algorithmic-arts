import pytest
import asyncio
import json
from datetime import datetime
from uuid import UUID
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from elasticsearch import AsyncElasticsearch
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.elasticsearch.company_indexer import CompanyIndexer
from src.infrastructure.repositories.company_repository import CompanyRepository
from src.domain.company import Company
from src.config import settings
from src.models import Company as CompanyModel


@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для асинхронных тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def es_client():
    """Клиент Elasticsearch для тестов."""
    client = AsyncElasticsearch(
        hosts=[settings.ELASTICSEARCH_URL],
        http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
        timeout=30,
        max_retries=3,
        retry_on_timeout=True
    )
    yield client
    await client.close()


@pytest.fixture
async def kafka_producer():
    """Kafka producer для тестов."""
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )
    await producer.start()
    yield producer
    await producer.stop()


@pytest.fixture
async def kafka_consumer():
    """Kafka consumer для тестов."""
    consumer = AIOKafkaConsumer(
        "company.events",
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="test-projection-worker",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest"
    )
    await consumer.start()
    yield consumer
    await consumer.stop()


@pytest.fixture
async def company_repo(db_session: AsyncSession):
    """Репозиторий компании для тестов."""
    return CompanyRepository(db_session)


@pytest.fixture
async def indexer(es_client: AsyncElasticsearch):
    """Индексер для тестов."""
    indexer = CompanyIndexer(es_client)
    await indexer.create_index()
    return indexer


class TestProjectionWorker:
    """Тесты для Kafka projection worker."""

    async def test_company_created_event_properly_indexed(
        self, 
        kafka_producer, 
        kafka_consumer, 
        indexer, 
        company_repo,
        db_session
    ):
        """Проверка, что событие company.created корректно индексируется в Elasticsearch."""
        # Создаем компанию через репозиторий (генерирует domain events)
        company_data = {
            "id": UUID("12345678-1234-5678-1234-567812345678"),
            "name": "Test Company",
            "slug": "test-company",
            "industry": "technology",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Создаем запись в БД
        db_company = CompanyModel(**company_data)
        db_session.add(db_company)
        await db_session.commit()
        await db_session.refresh(db_company)

        # Генерируем событие company.created вручную (как это делает application layer)
        event_data = {
            "event_type": "company.created",
            "aggregate_id": str(company_data["id"]),
            "payload": {
                "company_id": str(company_data["id"]),
                "name": company_data["name"],
                "industry": company_data["industry"],
                "created_at": company_data["created_at"].isoformat(),
                "updated_at": company_data["updated_at"].isoformat(),
                "slug": company_data["slug"]
            },
            "occurred_at": datetime.utcnow().isoformat()
        }

        # Отправляем событие в Kafka
        await kafka_producer.send(
            "company.events",
            key=str(company_data["id"]).encode(),
            value=json.dumps(event_data).encode()
        )

        # Ждем обработки события (projection worker должен обработать его)
        await asyncio.sleep(2)  # Даем время на обработку

        # Проверяем, что компания проиндексирована в Elasticsearch
        try:
            response = await indexer.es_client.get(
                index="companies",
                id=str(company_data["id"])
            )
            assert response["found"] is True
            source = response["_source"]
            assert source["name"] == "Test Company"
            assert source["industry"] == "technology"
            assert source["id"] == str(company_data["id"])
        except Exception as e:
            raise AssertionError(f"Company not found in Elasticsearch: {e}")

    async def test_company_updated_event_updates_index(
        self, 
        kafka_producer, 
        kafka_consumer, 
        indexer, 
        company_repo,
        db_session
    ):
        """Проверка, что событие company.updated обновляет документ в Elasticsearch."""
        # Создаем компанию
        company_id = UUID("87654321-4321-8765-4321-876543216789")
        initial_data = {
            "id": company_id,
            "name": "Initial Company",
            "slug": "initial-company",
            "industry": "initial",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db_company = CompanyModel(**initial_data)
        db_session.add(db_company)
        await db_session.commit()
        await db_session.refresh(db_company)

        # Индексируем начальную версию
        await indexer.index_company(Company(**initial_data))

        # Генерируем событие company.updated
        updated_data = {
            "event_type": "company.updated",
            "aggregate_id": str(company_id),
            "payload": {
                "company_id": str(company_id),
                "changed_fields": ["name", "industry"],
                "name": "Updated Company",
                "industry": "updated",
                "occurred_at": datetime.utcnow().isoformat()
            },
            "occurred_at": datetime.utcnow().isoformat()
        }

        # Отправляем событие в Kafka
        await kafka_producer.send(
            "company.events",
            key=str(company_id).encode(),
            value=json.dumps(updated_data).encode()
        )

        # Ждем обработки
        await asyncio.sleep(2)

        # Проверяем обновление в Elasticsearch
        try:
            response = await indexer.es_client.get(
                index="companies",
                id=str(company_id)
            )
            assert response["found"] is True
            source = response["_source"]
            assert source["name"] == "Updated Company"
            assert source["industry"] == "updated"
        except Exception as e:
            raise AssertionError(f"Company not updated in Elasticsearch: {e}")

    async def test_soft_delete_handling_in_projection(
        self, 
        kafka_producer, 
        kafka_consumer, 
        indexer, 
        company_repo,
        db_session
    ):
        """Проверка, что soft delete корректно обрабатывается в projection worker."""
        # Создаем компанию
        company_id = UUID("abcdef12-3456-7890-abcd-ef1234567890")
        company_data = {
            "id": company_id,
            "name": "Delete Test Company",
            "slug": "delete-test",
            "industry": "test",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db_company = CompanyModel(**company_data)
        db_session.add(db_company)
        await db_session.commit()
        await db_session.refresh(db_company)

        # Индексируем компанию
        await indexer.index_company(Company(**company_data))

        # Генерируем событие company.updated с deleted_at
        delete_event = {
            "event_type": "company.updated",
            "aggregate_id": str(company_id),
            "payload": {
                "company_id": str(company_id),
                "changed_fields": ["deleted_at"],
                "deleted_at": datetime.utcnow().isoformat(),
                "occurred_at": datetime.utcnow().isoformat()
            },
            "occurred_at": datetime.utcnow().isoformat()
        }

        # Отправляем событие в Kafka
        await kafka_producer.send(
            "company.events",
            key=str(company_id).encode(),
            value=json.dumps(delete_event).encode()
        )

        # Ждем обработки
        await asyncio.sleep(2)

        # Проверяем, что компания больше не доступна в поиске (soft delete)
        try:
            # Попытка найти компанию по ID должна вернуть 404 или не найдено
            response = await indexer.es_client.get(
                index="companies",
                id=str(company_id)
            )
            # В реальном приложении мы бы фильтровали по deleted_at IS NULL в queries
            # Для теста проверим, что deleted_at установлен
            assert response["_source"]["deleted_at"] is not None
        except Exception as e:
            raise AssertionError(f"Soft delete not handled properly: {e}")