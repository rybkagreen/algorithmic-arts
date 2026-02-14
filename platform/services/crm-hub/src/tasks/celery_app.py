import os

from celery import Celery

# Настройки Celery из переменных окружения
celery_app = Celery(
    "crm_hub",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=[
        "src.tasks.sync_tasks",
    ],
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "sync-crm-every-15-minutes": {
            "task": "src.tasks.sync_tasks.batch_sync_task",
            "schedule": 900.0,  # 15 минут в секундах
        },
        "refresh-expiring-tokens": {
            "task": "src.tasks.sync_tasks.refresh_tokens_task",
            "schedule": 3600.0,  # Каждый час
        },
    },
)
