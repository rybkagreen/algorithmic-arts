from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import ai
from .kafka.consumers import start_ai_consumers
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем Kafka consumer как фоновую задачу
    task = asyncio.create_task(start_ai_consumers())
    yield
    # Останавливаем задачу при завершении
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="AI Core Service",
    description="Мультиагентная система для платформы ALGORITHMIC ARTS",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(ai.router)