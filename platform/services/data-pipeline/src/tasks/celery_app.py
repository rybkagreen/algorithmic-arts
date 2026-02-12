from celery import Celery
from celery.schedules import crontab
from ..config import settings

celery_app = Celery(
    "data_pipeline",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "src.tasks.scrape_tasks",
        "src.tasks.process_tasks",
    ],
)

celery_app.conf.beat_schedule = {
    "scrape-vc-ru": {
        "task": "src.tasks.scrape_tasks.scrape_vc_ru_task",
        "schedule": crontab(minute="*/15"),  # каждые 15 минут
    },
    "scrape-rusbase": {
        "task": "src.tasks.scrape_tasks.scrape_rusbase_task",
        "schedule": crontab(minute="*/20"),  # каждые 20 минут
    },
    "scrape-habr-career": {
        "task": "src.tasks.scrape_tasks.scrape_habr_career_task",
        "schedule": crontab(minute=0, hour="*/2"),  # каждые 2 часа
    },
    "scrape-crunchbase": {
        "task": "src.tasks.scrape_tasks.scrape_crunchbase_task",
        "schedule": crontab(minute=30, hour="*/4"),  # каждые 4 часа
    },
    "process-raw-companies": {
        "task": "src.tasks.process_tasks.process_raw_company_task",
        "schedule": crontab(second="*/30"),  # каждые 30 секунд (для dev)
    },
}