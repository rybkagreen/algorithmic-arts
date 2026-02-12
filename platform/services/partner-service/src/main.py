"""Partner service main application."""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from shared.logging import get_logger
from shared.schemas import HealthCheckResponse
from .routers import partners

# Use shared logging configuration
logger = get_logger("partner-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Partner Service",
    description="Partnership management service for ALGORITHMIC ARTS platform",
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
app.include_router(partners.router)

# Health check
@app.get("/health")
async def health_check():
    return HealthCheckResponse(service="partner-service", version="1.0.0")