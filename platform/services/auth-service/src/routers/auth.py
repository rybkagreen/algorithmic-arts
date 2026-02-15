"""Auth routers for auth service."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.logging import get_logger
from .core.rate_limiter import limiter
from .dependencies import get_db
from .schemas.user import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    OAuthLoginRequest,
    OAuthLoginResponse,
)
from .services.auth_service import AuthService
from .services.oauth_service import OAuthService

logger = get_logger("auth-router")

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED, operation_id="registerUser")
@limiter.limit("10/hour")
async def register(
    request: Request,
    body: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(),
):
    """Register new user."""
    try:

        await auth_service.register(body)
        # В реальной реализации здесь будет отправка email через background task
        return {"message": "Регистрация успешна. Проверьте email для верификации."}
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(status_code=400, detail="Registration failed")


@router.post("/login", response_model=TokenResponse, operation_id="loginUser")
@limiter.limit("5/5minutes")
async def login(
    request: Request,
    body: LoginRequest,
    auth_service: AuthService = Depends(),
):
    """Login user and return tokens."""
    try:
        return await auth_service.authenticate(body)
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/refresh", response_model=TokenResponse, operation_id="refreshTokens")
async def refresh(
    body: RefreshRequest,
    auth_service: AuthService = Depends(),
):
    """Refresh tokens using refresh token."""
    try:
        return await auth_service.refresh_tokens(body.refresh_token)
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/oauth/login", response_model=OAuthLoginResponse, operation_id="oauthLogin")
@limiter.limit("10/hour")
async def oauth_login(
    request: Request,
    body: OAuthLoginRequest,
    oauth_service: OAuthService = Depends(),
):
    """OAuth login endpoint."""
    try:
        return await oauth_service.login_with_oauth(
            body.provider, body.code, body.redirect_uri
        )
    except Exception as e:
        logger.error("OAuth login failed", provider=body.provider, error=str(e))
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")


@router.get("/health", operation_id="healthCheck")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth-service"}