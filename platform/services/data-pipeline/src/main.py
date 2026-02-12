from fastapi import FastAPI
from contextlib import asynccontextmanager
from .kafka.consumers import start_data_consumers
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем Kafka consumer как фоновую задачу
    task = asyncio.create_task(start_data_consumers())
    yield
    # Останавливаем задачу при завершении
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Data Pipeline Service",
    description="ETL-пайплайн для сбора и нормализации данных о российских SaaS-компаниях",
    version="1.0.0",
    lifespan=lifespan
)

# Эндпоинты можно добавить позже