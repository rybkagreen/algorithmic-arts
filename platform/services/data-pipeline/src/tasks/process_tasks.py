from celery import current_app
from celery_app import celery_app
from ..transform.normalizer import normalize_company_data
from ..transform.deduplicator import find_duplicate
from ..load.db_loader import upsert_companies
from ..load.kafka_producer import KafkaProducer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import structlog

log = structlog.get_logger()

# Инициализация зависимостей
engine = create_async_engine("postgresql+asyncpg://data_pipeline:password@postgres:5432/data_pipeline")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
kafka_producer = KafkaProducer()

@celery_app.task(
    name="src.tasks.process_tasks.process_raw_company_task",
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
)
def process_raw_company_task(self, raw_company: dict):
    """Обрабатывает одну сырую компанию: нормализует, дедуплицирует, сохраняет."""
    try:
        # Нормализуем данные
        normalized = normalize_company_data(raw_company)
        
        # Получаем существующие компании для дедупликации
        async def get_existing_companies():
            async with async_session() as session:
                result = await session.execute("""
                    SELECT id, name, website, industry, tech_stack
                    FROM companies
                    WHERE deleted_at IS NULL
                    LIMIT 1000
                """)
                return [dict(r._mapping) for r in result.fetchall()]
        
        existing_companies = current_app.loop.run_until_complete(get_existing_companies())
        
        # Ищем дубликат
        duplicate = find_duplicate(normalized, existing_companies)
        if duplicate:
            log.info("duplicate_found", name=normalized["name"], duplicate_id=duplicate.get("id"))
            # Обновляем существующую запись (в db_loader это делается автоматически)
            normalized["id"] = duplicate.get("id")
        
        # Сохраняем в БД
        async def save_to_db():
            async with async_session() as session:
                new_ids = await upsert_companies(session, [normalized], kafka_producer)
                return new_ids
        
        new_ids = current_app.loop.run_until_complete(save_to_db())
        
        return {
            "status": "success",
            "company_name": normalized["name"],
            "new_id": new_ids[0] if new_ids else None,
            "is_duplicate": bool(duplicate),
        }
    except Exception as exc:
        log.error("process_failed", error=str(exc), company_name=raw_company.get("name"))
        raise self.retry(exc=exc)