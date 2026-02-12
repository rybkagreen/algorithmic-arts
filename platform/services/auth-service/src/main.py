from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from shared.logging import get_logger
from shared.schemas import HealthCheckResponse
from .config import settings
from .core.rate_limiter import limiter
from .routers import auth

# Use shared logging configuration
logger = get_logger("auth-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Auth Service",
    description="Authentication service for ALGORITHMIC ARTS platform",
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
app.state.limiter = limiter

# Метрики Prometheus
instrumentator = Instrumentator().instrument(app)


@app.get("/metrics")
async def metrics():
    return instrumentator.get_metrics()


# Регистрация роутеров
app.include_router(auth.router)


# Health check
@app.get("/health")
async def health_check():
    return HealthCheckResponse(service="auth-service", version="1.0.0")
