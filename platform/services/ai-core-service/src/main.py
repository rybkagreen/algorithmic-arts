"""AI Core service main application."""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from shared.logging import get_logger
from shared.schemas import HealthCheckResponse
from .routers import ai

# Use shared logging configuration
logger = get_logger("ai-core-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    pass

app = FastAPI(
    title="AI Core Service",
    description="AI agents and LLM orchestration service for ALGORITHMIC ARTS platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Метрики Prometheus
instrumentator = Instrumentator().instrument(app)

@app.get("/metrics")
async def metrics():
    return instrumentator.get_metrics()

# Регистрация роутеров
app.include_router(ai.router)

# Health check
@app.get("/health")
async def health_check():
    return HealthCheckResponse(service="ai-core-service", version="1.0.0")