from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .core.exceptions import (
    InvalidCredentialsError,
    RateLimitExceededError,
    UserNotFoundError,
)
from .core.rate_limiter import limiter
from .dependencies import get_db, get_jwt_service, get_user_repository
from .schemas.auth import (
    LoginRequest,
    PasswordConfirmRequest,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from .services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def register(
    request: Request,
    body: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(),
):
    user = await auth_service.register(body)
    # В реальной реализации здесь будет отправка email через background task
    return {"message": "Регистрация успешна. Проверьте email для верификации."}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/5minutes")
async def login(
    request: Request,
    body: LoginRequest,
    auth_service: AuthService = Depends(),
):
    return await auth_service.authenticate(body)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    auth_service: AuthService = Depends(),
):
    return await auth_service.refresh_tokens(body.refresh_token)


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}