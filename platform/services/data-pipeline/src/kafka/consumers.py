import json
import asyncio
from aiokafka import AIOKafkaConsumer
from tasks.process_tasks import process_raw_company_task
import structlog

log = structlog.get_logger()

TOPICS = ["company.raw_data"]

async def start_data_consumers():
    """Слушает company.raw_data → запускает process_raw_company_task."""
    consumer = AIOKafkaConsumer(
        *TOPICS,
        bootstrap_servers="kafka:9092",
        group_id="data-pipeline-service",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    await consumer.start()
    
    try:
        async for msg in consumer:
            raw_company = msg.value
            # Откладываем в Celery, не блокируем consumer
            process_raw_company_task.delay(raw_company)
            log.info("process_task_queued", company_name=raw_company.get("name"))
    finally:
        await consumer.stop()