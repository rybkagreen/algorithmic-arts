import json
from aiokafka import AIOKafkaConsumer
from tasks.enrichment import enrich_company_task

TOPICS = ["company.created"]


async def start_ai_consumers():
    """Запускает Kafka consumer для обработки событий."""
    consumer = AIOKafkaConsumer(
        *TOPICS,
        bootstrap_servers="kafka:9092",
        group_id="ai-core-service",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    await consumer.start()
    
    try:
        async for msg in consumer:
            event = msg.value
            # Формат события из промпта №3: {"company_id": "uuid", "name": "...", ...}
            company_id = event.get("company_id")
            if company_id:
                enrich_company_task.delay(company_id)
                # Не ждём результата — Celery сделает async
    finally:
        await consumer.stop()