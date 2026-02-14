from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from shared.logging import get_logger
from shared.schemas import HealthCheckResponse
from .presentation.routers import companies

# Use shared logging configuration
logger = get_logger("company-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Company Service",
    description="Company management service for ALGORITHMIC ARTS platform",
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
app.include_router(companies.router)

# Health check
@app.get("/health")
async def health_check():
    return HealthCheckResponse(service="company-service", version="1.0.0")