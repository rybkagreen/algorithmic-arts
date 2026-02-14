import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routers.crm import router as crm
from src.webhooks.router import router as webhook_router

# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)

log = structlog.get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CRM Hub Service для платформы ALGORITHMIC ARTS",
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Включаем маршруты
app.include_router(crm)
app.include_router(webhook_router)


@app.on_event("startup")
async def startup_event():
    log.info("crm_hub_service_startup", version=settings.APP_VERSION)

    # Запускаем Kafka consumer в фоновом режиме
    try:
        from .kafka.consumers import start_kafka_consumer

        await start_kafka_consumer()
        log.info("kafka_consumer_started")
    except Exception as e:
        log.error("kafka_consumer_start_error", error=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    log.info("crm_hub_service_shutdown")

    # Останавливаем Kafka consumer
    try:
        from .kafka.consumers import consumer

        await consumer.stop()
        log.info("kafka_consumer_stopped")
    except Exception as e:
        log.error("kafka_consumer_stop_error", error=str(e))


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса."""
    return {"status": "healthy", "service": "crm-hub", "version": settings.APP_VERSION}


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=8007, reload=True, log_level="info"
    )
