import json

import structlog
from aiokafka import AIOKafkaConsumer

from .config import settings
from .core.cache import UserCacheService
from .repositories.user_repository import UserRepository

logger = structlog.get_logger()


async def handle_billing_subscription_changed(event: dict):
    """При изменении подписки обновляем роль пользователя."""
    user_id = event["user_id"]
    new_plan = event["plan"]

    role_map = {
        "starter": "free_user",
        "growth": "paid_user",
        "scale": "paid_user",
        "enterprise": "company_admin",
    }

    new_role = role_map.get(new_plan, "free_user")
    
    # В реальной реализации здесь будет обновление роли в auth-service через API или Kafka
    logger.info("user_role_updated", user_id=user_id, new_role=new_role)


async def start_consumers():
    consumer = AIOKafkaConsumer(
        "billing.subscription_changed",
        bootstrap_servers=settings.kafka.bootstrap_servers,
        group_id=settings.kafka.consumer_group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    async for msg in consumer:
        await handle_billing_subscription_changed(msg.value)