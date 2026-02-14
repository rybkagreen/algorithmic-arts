from celery import Celery
from pydantic import BaseSettings

class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379/0"
    broker_url: str = "redis://redis:6379/1"
    result_backend: str = "redis://redis:6379/2"

settings = Settings()
celery_app = Celery(
    "ai_core",
    broker=settings.broker_url,
    backend=settings.result_backend,
    include=[
        "tasks.enrichment",
        "tasks.scouting",
        "tasks.embedding",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=False,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)