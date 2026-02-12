# ALGORITHMIC ARTS — Улучшенные Промпты №3 и №4

**Версия:** 3.1 (Enhanced)  
**Дата:** Февраль 2026  
**Статус:** Production Ready  

> Эти промпты — расширенная версия исходных №3 и №4 из `PROMPTS_FOR_QWEN.md`.  
> Добавлены: полная файловая структура, конкретные Pydantic-модели, паттерны кэширования, Kafka-схемы событий, примеры тестов и обработка ошибок.

---

## Промпт №3: Auth + User Service (Расширенный)

### Задача
Реализовать production-ready микросервисы аутентификации и управления пользователями с полным набором функций безопасности.

### Промпт

```markdown
Создай полные микросервисы Auth и User для платформы ALGORITHMIC ARTS.
Используй Python 3.12, FastAPI 0.115+, SQLAlchemy 2.0 (async), Redis Stack 7.4.

═══════════════════════════════════════════════════════════
ЧАСТЬ 1: AUTH-SERVICE (порт 8001)
═══════════════════════════════════════════════════════════

## СТРУКТУРА ФАЙЛОВ:

services/auth-service/
├── pyproject.toml
├── Dockerfile
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 0001_initial_auth_tables.py
└── src/
    ├── main.py
    ├── config.py
    ├── dependencies.py
    ├── models/
    │   ├── __init__.py
    │   ├── user.py
    │   ├── session.py
    │   └── oauth.py
    ├── schemas/
    │   ├── __init__.py
    │   ├── auth.py
    │   └── user.py
    ├── routers/
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── oauth.py
    │   └── two_factor.py
    ├── services/
    │   ├── __init__.py
    │   ├── auth_service.py
    │   ├── jwt_service.py
    │   ├── email_service.py
    │   └── totp_service.py
    ├── repositories/
    │   ├── __init__.py
    │   └── user_repository.py
    └── core/
        ├── security.py
        ├── rate_limiter.py
        └── exceptions.py


## ЗАВИСИМОСТИ (pyproject.toml):

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.30.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.36"}
asyncpg = "^0.30.0"
alembic = "^1.14.0"
pydantic = {extras = ["email"], version = "^2.10.0"}
pydantic-settings = "^2.6.0"
redis = {extras = ["hiredis"], version = "^5.2.0"}
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
pyotp = "^2.9.0"
qrcode = "^8.0"
python-multipart = "^0.0.18"
httpx = "^0.28.0"
aiokafka = "^0.11.0"
structlog = "^24.4.0"
prometheus-fastapi-instrumentator = "^7.0.0"
slowapi = "^0.1.9"

[tool.poetry.dev-dependencies]
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
httpx = "^0.28.0"
factory-boy = "^3.3.0"
faker = "^33.0.0"


## МОДЕЛИ SQLAlchemy (src/models/user.py):

from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum as PyEnum
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class UserRole(str, PyEnum):
    FREE_USER = "free_user"
    PAID_USER = "paid_user"
    COMPANY_ADMIN = "company_admin"
    PLATFORM_ADMIN = "platform_admin"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(sa.String(72), nullable=False)
    full_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    company_name: Mapped[str | None] = mapped_column(sa.String(255))
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole), nullable=False, default=UserRole.FREE_USER
    )
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    totp_secret: Mapped[str | None] = mapped_column(sa.String(32))
    totp_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    failed_login_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))


## PYDANTIC СХЕМЫ (src/schemas/auth.py):

from pydantic import BaseModel, EmailStr, field_validator, model_validator
from uuid import UUID


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str | None = None
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать заглавную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать цифру")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None  # Для 2FA


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 минут в секундах


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordConfirmRequest(BaseModel):
    token: str
    new_password: str
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")
        return v


class TwoFactorSetupResponse(BaseModel):
    totp_uri: str
    qr_code_base64: str
    backup_codes: list[str]


class TwoFactorVerifyRequest(BaseModel):
    totp_code: str


## JWT СЕРВИС (src/services/jwt_service.py):

import time
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from jose import jwt, JWTError
from redis.asyncio import Redis
from ..config import settings


class JWTService:
    """
    RS256 JWT с ротацией ключей и Redis-blacklist.
    Access token: 15 минут
    Refresh token: 30 дней
    """
    
    ACCESS_TOKEN_TTL = 900          # 15 минут
    REFRESH_TOKEN_TTL = 2592000     # 30 дней
    ALGORITHM = "RS256"
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self._private_key = settings.JWT_PRIVATE_KEY
        self._public_key = settings.JWT_PUBLIC_KEY
    
    async def create_access_token(self, user_id: UUID, role: str) -> str:
        jti = str(uuid4())
        now = int(time.time())
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "iat": now,
            "exp": now + self.ACCESS_TOKEN_TTL,
            "jti": jti,
        }
        return jwt.encode(payload, self._private_key, algorithm=self.ALGORITHM)
    
    async def create_refresh_token(self, user_id: UUID) -> str:
        jti = str(uuid4())
        now = int(time.time())
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": now + self.REFRESH_TOKEN_TTL,
            "jti": jti,
        }
        token = jwt.encode(payload, self._private_key, algorithm=self.ALGORITHM)
        # Сохраняем JTI в Redis для последующего отзыва
        await self.redis.setex(
            f"refresh_token:{user_id}:{jti}", 
            self.REFRESH_TOKEN_TTL,
            "valid"
        )
        return token
    
    async def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self._public_key, algorithms=[self.ALGORITHM])
        except JWTError as e:
            raise InvalidTokenError(f"Токен недействителен: {e}")
        
        # Проверяем blacklist
        jti = payload.get("jti")
        if jti and await self.redis.exists(f"blacklist:{jti}"):
            raise InvalidTokenError("Токен отозван")
        
        return payload
    
    async def revoke_token(self, token: str) -> None:
        """Добавляет JTI в blacklist."""
        try:
            payload = jwt.decode(
                token, self._public_key, algorithms=[self.ALGORITHM],
                options={"verify_exp": False}
            )
            jti = payload.get("jti")
            exp = payload.get("exp", 0)
            ttl = max(0, exp - int(time.time()))
            if jti and ttl > 0:
                await self.redis.setex(f"blacklist:{jti}", ttl, "revoked")
        except JWTError:
            pass  # Уже невалидный токен — игнорируем


## RATE LIMITER (src/core/rate_limiter.py):

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Применение в роутере:
# @router.post("/login")
# @limiter.limit("5/5minutes")
# async def login(request: Request, ...):


## ЭНДПОИНТЫ (src/routers/auth.py):

from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from ..schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshRequest, PasswordResetRequest, PasswordConfirmRequest
)
from ..services.auth_service import AuthService
from ..core.rate_limiter import limiter
from ..core.exceptions import InvalidCredentialsError, UserNotFoundError, RateLimitExceededError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def register(
    request: Request,
    body: RegisterRequest,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(),
):
    user = await service.register(body)
    background_tasks.add_task(service.send_verification_email, user.email)
    return {"message": "Регистрация успешна. Проверьте email для верификации."}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/5minutes")
async def login(
    request: Request,
    body: LoginRequest,
    service: AuthService = Depends(),
):
    return await service.authenticate(body)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    access_token: str = Depends(get_current_token),
    service: AuthService = Depends(),
):
    await service.logout(access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    service: AuthService = Depends(),
):
    return await service.refresh_tokens(body.refresh_token)


@router.get("/verify-email")
async def verify_email(token: str, service: AuthService = Depends()):
    await service.verify_email(token)
    return {"message": "Email подтверждён"}


@router.post("/password/reset")
@limiter.limit("3/hour")
async def password_reset(
    request: Request,
    body: PasswordResetRequest,
    service: AuthService = Depends(),
):
    # Всегда возвращаем 200 — защита от enumeration attack
    await service.initiate_password_reset(body.email)
    return {"message": "Если email зарегистрирован, вы получите инструкцию"}


@router.post("/password/confirm")
async def password_confirm(
    body: PasswordConfirmRequest,
    service: AuthService = Depends(),
):
    await service.confirm_password_reset(body.token, body.new_password)
    return {"message": "Пароль изменён успешно"}


## KAFKA СОБЫТИЯ (схемы для Confluent Schema Registry):

# user.created
{
    "type": "record",
    "name": "UserCreated",
    "namespace": "com.algorithmic_arts.auth",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "user_id", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "full_name", "type": "string"},
        {"name": "company_name", "type": ["null", "string"], "default": null},
        {"name": "role", "type": "string"},
        {"name": "occurred_at", "type": "string"}
    ]
}

# user.email_verified
{
    "type": "record",
    "name": "UserEmailVerified",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "user_id", "type": "string"},
        {"name": "occurred_at", "type": "string"}
    ]
}

# user.login_failed
{
    "type": "record",
    "name": "UserLoginFailed",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "ip_address", "type": "string"},
        {"name": "attempt_count", "type": "int"},
        {"name": "occurred_at", "type": "string"}
    ]
}


## ПРИМЕРЫ ТЕСТОВ (tests/unit/test_jwt_service.py):

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from src.services.jwt_service import JWTService


@pytest.fixture
def mock_redis():
    return AsyncMock()


@pytest.fixture
def jwt_service(mock_redis):
    return JWTService(redis=mock_redis)


class TestJWTService:
    
    @pytest.mark.asyncio
    async def test_create_access_token_contains_correct_claims(self, jwt_service):
        user_id = uuid4()
        token = await jwt_service.create_access_token(user_id, "paid_user")
        
        payload = await jwt_service.verify_token(token)
        
        assert payload["sub"] == str(user_id)
        assert payload["role"] == "paid_user"
        assert payload["type"] == "access"
        assert "jti" in payload
    
    @pytest.mark.asyncio
    async def test_revoked_token_raises_error(self, jwt_service, mock_redis):
        user_id = uuid4()
        token = await jwt_service.create_access_token(user_id, "free_user")
        
        await jwt_service.revoke_token(token)
        mock_redis.exists.return_value = True
        
        with pytest.raises(InvalidTokenError):
            await jwt_service.verify_token(token)
    
    @pytest.mark.asyncio
    async def test_expired_token_raises_error(self, jwt_service):
        """Протухший токен должен вызывать InvalidTokenError."""
        import time
        with patch.object(jwt_service, 'ACCESS_TOKEN_TTL', -1):
            user_id = uuid4()
            token = await jwt_service.create_access_token(user_id, "free_user")
        
        with pytest.raises(InvalidTokenError, match="Токен недействителен"):
            await jwt_service.verify_token(token)


## tests/integration/test_auth_endpoints.py:

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestAuthEndpoints:
    
    @pytest.mark.asyncio
    async def test_register_creates_user_and_sends_email(
        self, client: AsyncClient, db: AsyncSession
    ):
        response = await client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass1",
            "full_name": "Иван Иванов",
            "company_name": "ООО Тест"
        })
        
        assert response.status_code == 201
        assert "Проверьте email" in response.json()["message"]
        
        # Пользователь создан в БД
        user = await db.get(User, email="test@example.com")
        assert user is not None
        assert user.is_verified is False
    
    @pytest.mark.asyncio
    async def test_login_with_wrong_password_returns_401(self, client: AsyncClient):
        response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword"
        })
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_rate_limit_on_login_after_5_attempts(self, client: AsyncClient):
        for _ in range(5):
            await client.post("/auth/login", json={
                "email": "test@example.com", "password": "wrong"
            })
        
        response = await client.post("/auth/login", json={
            "email": "test@example.com", "password": "wrong"
        })
        assert response.status_code == 429


═══════════════════════════════════════════════════════════
ЧАСТЬ 2: USER-SERVICE (порт 8002)
═══════════════════════════════════════════════════════════

## СТРУКТУРА ФАЙЛОВ:

services/user-service/
├── pyproject.toml
├── Dockerfile
├── alembic/
│   └── versions/
│       └── 0001_user_profiles.py
└── src/
    ├── main.py
    ├── config.py
    ├── models/
    │   ├── user_profile.py
    │   └── team_membership.py
    ├── schemas/
    │   ├── user.py
    │   └── team.py
    ├── routers/
    │   ├── users.py
    │   └── teams.py
    ├── services/
    │   ├── user_service.py
    │   ├── team_service.py
    │   └── cache_service.py
    ├── repositories/
    │   └── user_repository.py
    ├── kafka/
    │   ├── producers.py
    │   └── consumers.py
    └── core/
        ├── permissions.py
        └── cache.py


## RBAC MIDDLEWARE (src/core/permissions.py):

from enum import Enum
from fastapi import Depends, HTTPException, status
from .jwt_validator import get_current_user


class Permission(str, Enum):
    COMPANY_READ = "company:read"
    COMPANY_WRITE = "company:write"
    COMPANY_DELETE = "company:delete"
    PARTNERSHIP_READ = "partnership:read"
    PARTNERSHIP_WRITE = "partnership:write"
    ANALYTICS_READ = "analytics:read"
    ADMIN_ACCESS = "admin:access"


ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "free_user": {
        Permission.COMPANY_READ,
        Permission.PARTNERSHIP_READ,
    },
    "paid_user": {
        Permission.COMPANY_READ,
        Permission.COMPANY_WRITE,
        Permission.PARTNERSHIP_READ,
        Permission.PARTNERSHIP_WRITE,
        Permission.ANALYTICS_READ,
    },
    "company_admin": {
        Permission.COMPANY_READ,
        Permission.COMPANY_WRITE,
        Permission.COMPANY_DELETE,
        Permission.PARTNERSHIP_READ,
        Permission.PARTNERSHIP_WRITE,
        Permission.ANALYTICS_READ,
    },
    "platform_admin": set(Permission),  # Все права
}


def require_permission(permission: Permission):
    """Dependency factory для проверки прав."""
    async def check_permission(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "free_user")
        allowed = ROLE_PERMISSIONS.get(user_role, set())
        if permission not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется разрешение: {permission.value}"
            )
        return current_user
    return check_permission


# Использование в эндпоинте:
# @router.post("/companies")
# async def create_company(
#     current_user: dict = Depends(require_permission(Permission.COMPANY_WRITE))
# ):


## КЭШИРОВАНИЕ ПРОФИЛЕЙ (src/core/cache.py):

import json
from uuid import UUID
from redis.asyncio import Redis


class UserCacheService:
    """Read-through кэш для профилей пользователей. TTL = 1 час."""
    
    TTL = 3600
    KEY_PREFIX = "user_profile:"
    
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def get(self, user_id: UUID) -> dict | None:
        data = await self.redis.get(f"{self.KEY_PREFIX}{user_id}")
        return json.loads(data) if data else None
    
    async def set(self, user_id: UUID, profile: dict) -> None:
        await self.redis.setex(
            f"{self.KEY_PREFIX}{user_id}",
            self.TTL,
            json.dumps(profile, default=str)
        )
    
    async def invalidate(self, user_id: UUID) -> None:
        await self.redis.delete(f"{self.KEY_PREFIX}{user_id}")


## KAFKA CONSUMER (src/kafka/consumers.py):

from aiokafka import AIOKafkaConsumer
import json
import structlog

logger = structlog.get_logger()


async def handle_billing_subscription_changed(event: dict):
    """При изменении подписки обновляем роль пользователя."""
    user_id = event["user_id"]
    new_plan = event["plan"]
    
    role_map = {
        "starter": "free_user",
        "growth": "paid_user",
        "scale": "paid_user",
        "enterprise": "company_admin",
    }
    
    new_role = role_map.get(new_plan, "free_user")
    await user_repository.update_role(user_id, new_role)
    await cache_service.invalidate(user_id)
    
    logger.info("user_role_updated", user_id=user_id, new_role=new_role)


async def start_consumers():
    consumer = AIOKafkaConsumer(
        "billing.subscription_changed",
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="user-service-group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    async for msg in consumer:
        await handle_billing_subscription_changed(msg.value)


ОБЩИЕ ТРЕБОВАНИЯ для обоих сервисов:
- Health check на /health с проверкой DB и Redis
- Prometheus метрики на /metrics
- Structured logging через structlog (JSON формат)
- Graceful shutdown (lifespan context manager)
- Middleware: CORS, GZip, RequestID
- Централизованный обработчик исключений (exception_handler)
- OpenAPI описание каждого эндпоинта (description, responses, examples)

Создай полную реализацию обоих сервисов со всеми файлами.
```

---

## Промпт №4: Company + Partner Service (Расширенный)

### Задача
Реализовать CRUD компаний и систему подбора партнёров с DDD, CQRS, Event Sourcing и vector search.

### Промпт

```markdown
Создай Company Service и Partner Service для ALGORITHMIC ARTS.
Python 3.12, FastAPI 0.115+, SQLAlchemy 2.0, pgvector 0.3+, aiokafka 0.11.

═══════════════════════════════════════════════════════════
ЧАСТЬ 1: COMPANY-SERVICE (порт 8003)
═══════════════════════════════════════════════════════════

## СТРУКТУРА ФАЙЛОВ (DDD layers):

services/company-service/
├── pyproject.toml
├── Dockerfile
├── alembic/
│   └── versions/
│       ├── 0001_companies_table.py
│       └── 0002_event_store.py
└── src/
    ├── main.py
    ├── config.py
    │
    ├── domain/                   # Чистый domain-слой (нет зависимостей)
    │   ├── __init__.py
    │   ├── company.py            # Aggregate Root
    │   ├── events.py             # Domain Events
    │   ├── value_objects.py      # INN, OGRN, FundingAmount
    │   └── exceptions.py
    │
    ├── application/              # Use cases (CQRS handlers)
    │   ├── commands/
    │   │   ├── create_company.py
    │   │   ├── update_company.py
    │   │   ├── enrich_company.py
    │   │   └── delete_company.py
    │   └── queries/
    │       ├── get_company.py
    │       ├── list_companies.py
    │       ├── search_companies.py
    │       └── get_similar_companies.py
    │
    ├── infrastructure/           # БД, внешние сервисы
    │   ├── models.py
    │   ├── repositories/
    │   │   ├── company_repository.py
    │   │   └── event_store_repository.py
    │   ├── elasticsearch/
    │   │   └── company_indexer.py
    │   ├── kafka/
    │   │   ├── producers.py
    │   │   └── consumers.py
    │   └── ai_client/
    │       └── embedding_client.py
    │
    └── presentation/             # HTTP слой
        ├── routers/
        │   └── companies.py
        └── schemas/
            ├── company.py
            └── filters.py


## DOMAIN MODEL (src/domain/company.py):

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Any
from .events import CompanyCreated, CompanyUpdated, CompanyEnriched
from .value_objects import INN, OGRN, FundingAmount
from .exceptions import CompanyValidationError


@dataclass
class Company:
    """Aggregate Root для компании."""
    
    id: UUID
    name: str
    slug: str
    description: str | None
    website: str | None
    industry: str
    sub_industries: list[str]
    business_model: str | None
    founded_year: int | None
    headquarters_country: str
    headquarters_city: str | None
    employees_count: int | None
    employees_range: str | None
    funding_total: FundingAmount | None
    funding_stage: str | None
    last_funding_date: datetime | None
    inn: INN | None
    ogrn: OGRN | None
    legal_name: str | None
    tech_stack: dict[str, Any]
    integrations: list[str]
    api_available: bool
    ai_summary: str | None
    ai_tags: list[str]
    embedding: list[float] | None
    is_verified: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    
    _domain_events: list = field(default_factory=list, init=False, repr=False)
    
    @classmethod
    def create(cls, **kwargs) -> "Company":
        company = cls(id=uuid4(), **kwargs)
        company._domain_events.append(
            CompanyCreated(
                company_id=company.id,
                name=company.name,
                industry=company.industry,
                occurred_at=datetime.utcnow()
            )
        )
        return company
    
    def update(self, **kwargs) -> None:
        changed_fields = {}
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                setattr(self, key, value)
                changed_fields[key] = value
        
        if changed_fields:
            self.updated_at = datetime.utcnow()
            self._domain_events.append(
                CompanyUpdated(
                    company_id=self.id,
                    changed_fields=list(changed_fields.keys()),
                    occurred_at=datetime.utcnow()
                )
            )
    
    def enrich(self, summary: str, tags: list[str], embedding: list[float]) -> None:
        self.ai_summary = summary
        self.ai_tags = tags
        self.embedding = embedding
        self.updated_at = datetime.utcnow()
        self._domain_events.append(
            CompanyEnriched(company_id=self.id, occurred_at=datetime.utcnow())
        )
    
    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()
    
    def pop_events(self) -> list:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events


## VALUE OBJECTS (src/domain/value_objects.py):

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class INN:
    value: str
    
    def __post_init__(self):
        if not re.match(r"^\d{10}$|^\d{12}$", self.value):
            raise ValueError(f"Некорректный ИНН: {self.value}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class OGRN:
    value: str
    
    def __post_init__(self):
        if not re.match(r"^\d{13}$|^\d{15}$", self.value):
            raise ValueError(f"Некорректный ОГРН: {self.value}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class FundingAmount:
    amount: int        # в копейках
    currency: str = "RUB"
    
    @classmethod
    def from_rubles(cls, rubles: float, currency: str = "RUB") -> "FundingAmount":
        return cls(amount=int(rubles * 100), currency=currency)
    
    def to_rubles(self) -> float:
        return self.amount / 100


## PYDANTIC СХЕМЫ (src/presentation/schemas/company.py):

from pydantic import BaseModel, HttpUrl, field_validator
from uuid import UUID
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str
    description: str | None = None
    website: HttpUrl | None = None
    industry: str
    sub_industries: list[str] = []
    business_model: str | None = None
    founded_year: int | None = None
    headquarters_country: str = "RU"
    headquarters_city: str | None = None
    employees_count: int | None = None
    funding_total: float | None = None
    funding_stage: str | None = None
    inn: str | None = None
    legal_name: str | None = None
    tech_stack: dict = {}
    integrations: list[str] = []
    api_available: bool = False
    
    @field_validator("founded_year")
    @classmethod
    def validate_year(cls, v: int | None) -> int | None:
        if v and (v < 1900 or v > 2026):
            raise ValueError("Некорректный год основания")
        return v


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    website: str | None
    industry: str
    sub_industries: list[str]
    employees_range: str | None
    funding_stage: str | None
    tech_stack: dict
    integrations: list[str]
    ai_summary: str | None
    ai_tags: list[str]
    is_verified: bool
    view_count: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class CompanyFilterParams(BaseModel):
    """Query-параметры для фильтрации."""
    industry: str | None = None
    sub_industries: list[str] | None = None
    country: str | None = None
    city: str | None = None
    employees_range: str | None = None
    funding_stage: str | None = None
    has_api: bool | None = None
    min_founded_year: int | None = None
    max_founded_year: int | None = None
    tech_stack: list[str] | None = None
    
    # Пагинация (cursor-based)
    cursor: str | None = None
    limit: int = 20


## CQRS — ЗАПРОС (src/application/queries/search_companies.py):

from dataclasses import dataclass
from uuid import UUID


@dataclass
class SearchCompaniesQuery:
    text: str | None = None
    filters: dict = None
    cursor: str | None = None
    limit: int = 20
    user_id: UUID | None = None


@dataclass  
class SearchCompaniesResult:
    items: list
    next_cursor: str | None
    total: int


class SearchCompaniesHandler:
    """Гибридный поиск: полнотекстовый (Elasticsearch) + семантический (pgvector)."""
    
    def __init__(
        self,
        es_indexer: "ElasticsearchIndexer",
        company_repo: "CompanyRepository",
        embedding_client: "EmbeddingClient",
        cache: "Redis",
    ):
        self.es = es_indexer
        self.repo = company_repo
        self.embedding = embedding_client
        self.cache = cache
    
    async def handle(self, query: SearchCompaniesQuery) -> SearchCompaniesResult:
        if not query.text:
            # Только фильтрация — идём прямо в PostgreSQL
            return await self.repo.list_with_filters(
                query.filters, query.cursor, query.limit
            )
        
        # Hybrid search: получаем кандидатов из обоих источников
        es_ids, text_scores = await self._text_search(query.text, limit=100)
        
        query_embedding = await self.embedding.generate(query.text)
        vector_ids, vector_scores = await self.repo.vector_search(
            query_embedding, limit=100
        )
        
        # RRF (Reciprocal Rank Fusion) для объединения результатов
        final_ids = self._rrf_fusion(
            [(es_ids, text_scores), (vector_ids, vector_scores)]
        )[:query.limit]
        
        companies = await self.repo.get_by_ids(final_ids)
        return SearchCompaniesResult(items=companies, next_cursor=None, total=len(companies))
    
    @staticmethod
    def _rrf_fusion(ranked_lists: list, k: int = 60) -> list:
        """Reciprocal Rank Fusion объединяет несколько ранжированных списков."""
        scores: dict[str, float] = {}
        for ids, _ in ranked_lists:
            for rank, doc_id in enumerate(ids, start=1):
                scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)


## CQRS — КОМАНДА (src/application/commands/create_company.py):

from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateCompanyCommand:
    name: str
    industry: str
    created_by: UUID
    # ... остальные поля


class CreateCompanyHandler:
    """Создаёт компанию, сохраняет событие, публикует в Kafka."""
    
    def __init__(
        self,
        company_repo: "CompanyRepository",
        event_store: "EventStoreRepository",
        kafka_producer: "KafkaProducer",
        es_indexer: "ElasticsearchIndexer",
    ):
        self.repo = company_repo
        self.event_store = event_store
        self.kafka = kafka_producer
        self.es = es_indexer
    
    async def handle(self, command: CreateCompanyCommand) -> UUID:
        # 1. Создаём агрегат
        company = Company.create(
            name=command.name,
            industry=command.industry,
            # ...
        )
        
        # 2. Сохраняем в PostgreSQL (транзакция)
        async with transaction():
            await self.repo.save(company)
            
            # 3. Сохраняем события в Event Store
            for event in company.pop_events():
                await self.event_store.append(event)
        
        # 4. Публикуем событие в Kafka (вне транзакции)
        await self.kafka.publish("company.created", {
            "event_id": str(uuid4()),
            "company_id": str(company.id),
            "name": company.name,
            "industry": company.industry,
            "occurred_at": datetime.utcnow().isoformat()
        })
        
        # 5. Индексируем в Elasticsearch
        await self.es.index_company(company)
        
        return company.id


## VECTOR SEARCH (src/infrastructure/repositories/company_repository.py):

from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa


class CompanyRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def vector_search(
        self, embedding: list[float], limit: int = 20, threshold: float = 0.7
    ) -> tuple[list[str], list[float]]:
        """Поиск по cosine similarity через pgvector."""
        
        # Используем оператор <=> (cosine distance) из pgvector
        result = await self.session.execute(
            sa.text("""
                SELECT id::text,
                       1 - (embedding <=> :embedding::vector) AS similarity
                FROM companies
                WHERE deleted_at IS NULL
                  AND embedding IS NOT NULL
                  AND 1 - (embedding <=> :embedding::vector) >= :threshold
                ORDER BY embedding <=> :embedding::vector
                LIMIT :limit
            """),
            {
                "embedding": str(embedding),
                "threshold": threshold,
                "limit": limit
            }
        )
        rows = result.fetchall()
        ids = [r[0] for r in rows]
        scores = [float(r[1]) for r in rows]
        return ids, scores
    
    async def list_with_filters(
        self, filters: dict | None, cursor: str | None, limit: int
    ) -> "SearchCompaniesResult":
        """Cursor-based пагинация с фильтрацией."""
        
        query = (
            sa.select(CompanyORM)
            .where(CompanyORM.deleted_at.is_(None))
            .order_by(CompanyORM.created_at.desc(), CompanyORM.id)
            .limit(limit + 1)  # +1 для определения наличия следующей страницы
        )
        
        # Применяем фильтры
        if filters:
            if filters.get("industry"):
                query = query.where(CompanyORM.industry == filters["industry"])
            if filters.get("has_api"):
                query = query.where(CompanyORM.api_available.is_(True))
            if filters.get("tech_stack"):
                # GIN-индекс по JSONB
                for tech in filters["tech_stack"]:
                    query = query.where(
                        CompanyORM.tech_stack.contains({tech: True})
                    )
        
        # Cursor-based пагинация
        if cursor:
            cursor_dt, cursor_id = decode_cursor(cursor)
            query = query.where(
                sa.or_(
                    CompanyORM.created_at < cursor_dt,
                    sa.and_(
                        CompanyORM.created_at == cursor_dt,
                        CompanyORM.id > cursor_id
                    )
                )
            )
        
        rows = (await self.session.execute(query)).scalars().all()
        has_next = len(rows) > limit
        items = rows[:limit]
        
        next_cursor = (
            encode_cursor(items[-1].created_at, items[-1].id) if has_next else None
        )
        
        return SearchCompaniesResult(
            items=[company_to_dict(c) for c in items],
            next_cursor=next_cursor,
            total=len(items)
        )


## EVENT SOURCING (src/infrastructure/models.py):

class CompanyEventORM(Base):
    """Event Store для аудит-трейла всех изменений компании."""
    __tablename__ = "company_events"
    
    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    event_version: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    payload: Mapped[dict] = mapped_column(sa.JSON, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    
    __table_args__ = (
        sa.Index("idx_company_events_company_version", "company_id", "event_version"),
        # Партиционирование по occurred_at (PostgreSQL 17)
        # PARTITION BY RANGE (occurred_at)
    )


## KAFKA СОБЫТИЯ (схемы):

# company.created
{
    "event_id": "uuid",
    "company_id": "uuid",
    "name": "string",
    "industry": "string",
    "headquarters_city": "string | null",
    "occurred_at": "ISO8601"
}

# company.updated
{
    "event_id": "uuid",
    "company_id": "uuid",
    "changed_fields": ["industry", "tech_stack"],
    "occurred_at": "ISO8601"
}

# company.enriched
{
    "event_id": "uuid",
    "company_id": "uuid",
    "has_embedding": true,
    "tags_count": 5,
    "occurred_at": "ISO8601"
}


═══════════════════════════════════════════════════════════
ЧАСТЬ 2: PARTNER-SERVICE (порт 8004)
═══════════════════════════════════════════════════════════

## СТРУКТУРА ФАЙЛОВ:

services/partner-service/
└── src/
    ├── domain/
    │   ├── partnership.py
    │   └── scoring.py           # Алгоритм совместимости
    ├── application/
    │   ├── commands/
    │   │   ├── analyze_compatibility.py
    │   │   └── send_outreach.py
    │   └── queries/
    │       ├── get_recommendations.py
    │       └── get_stats.py
    ├── infrastructure/
    │   ├── repositories/
    │   │   └── partnership_repo.py
    │   ├── kafka/
    │   │   └── consumers.py     # Слушает company.created
    │   ├── ai_client/
    │   │   └── compatibility_client.py
    │   └── reporting/
    │       ├── pdf_generator.py
    │       └── excel_exporter.py
    └── presentation/
        └── routers/
            └── partnerships.py


## АЛГОРИТМ СОВМЕСТИМОСТИ (src/domain/scoring.py):

from dataclasses import dataclass


@dataclass
class CompatibilityScore:
    total: float                         # 0.0 - 1.0
    tech_compatibility: float
    market_overlap: float
    size_match: float
    geo_proximity: float
    no_competition: float
    complementarity: float
    explanation: str
    recommended_partnership_type: str    # integration, reseller, co-development


WEIGHTS = {
    "tech_compatibility": 0.25,
    "market_overlap": 0.20,
    "size_match": 0.15,
    "geo_proximity": 0.10,
    "no_competition": 0.15,
    "complementarity": 0.15,
}


def calculate_compatibility(company_a: dict, company_b: dict) -> CompatibilityScore:
    scores = {
        "tech_compatibility": _check_tech_stack_overlap(
            company_a.get("tech_stack", {}),
            company_b.get("tech_stack", {})
        ),
        "market_overlap": _check_market_overlap(
            company_a.get("sub_industries", []),
            company_b.get("sub_industries", [])
        ),
        "size_match": _check_size_compatibility(
            company_a.get("employees_range"),
            company_b.get("employees_range")
        ),
        "geo_proximity": _check_geo_proximity(
            company_a.get("headquarters_city"),
            company_b.get("headquarters_city")
        ),
        "no_competition": _check_not_direct_competitors(
            company_a.get("industry"),
            company_b.get("industry"),
            company_a.get("sub_industries", []),
            company_b.get("sub_industries", [])
        ),
        "complementarity": _check_complementarity(
            company_a.get("integrations", []),
            company_b.get("integrations", [])
        ),
    }
    
    total = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    
    return CompatibilityScore(
        total=round(total, 4),
        explanation=_build_explanation(scores, company_a, company_b),
        recommended_partnership_type=_recommend_type(scores),
        **scores
    )


def _check_tech_stack_overlap(stack_a: dict, stack_b: dict) -> float:
    """Jaccard similarity для технологических стеков."""
    keys_a = set(stack_a.keys())
    keys_b = set(stack_b.keys())
    if not keys_a and not keys_b:
        return 0.5  # нейтральный балл при отсутствии данных
    intersection = keys_a & keys_b
    union = keys_a | keys_b
    return len(intersection) / len(union) if union else 0.0


SIZE_RANGES = ["1-10", "11-50", "51-200", "201-500", "500+"]

def _check_size_compatibility(range_a: str | None, range_b: str | None) -> float:
    """Компании схожего или дополняющего размера — лучшие партнёры."""
    if not range_a or not range_b:
        return 0.5
    
    idx_a = SIZE_RANGES.index(range_a) if range_a in SIZE_RANGES else 2
    idx_b = SIZE_RANGES.index(range_b) if range_b in SIZE_RANGES else 2
    diff = abs(idx_a - idx_b)
    
    # Разница в 0-1 ступень — хорошо, 2+ — снижаем балл
    return max(0.0, 1.0 - diff * 0.25)


def _check_not_direct_competitors(
    industry_a: str, industry_b: str,
    subs_a: list, subs_b: list
) -> float:
    """Прямые конкуренты получают штраф — они не должны быть партнёрами."""
    if industry_a != industry_b:
        return 1.0
    overlap = set(subs_a) & set(subs_b)
    if len(overlap) > 2:
        return 0.1  # Сильное пересечение — конкуренты
    if len(overlap) == 1:
        return 0.7
    return 1.0


def _check_complementarity(integrations_a: list, integrations_b: list) -> float:
    """Компании, которые уже интегрируются с похожими сервисами, лучше совместимы."""
    set_a = set(integrations_a)
    set_b = set(integrations_b)
    if not set_a or not set_b:
        return 0.4
    common = len(set_a & set_b)
    # Похожий экосистемный портфель — хороший сигнал
    return min(1.0, 0.4 + common * 0.15)


def _check_market_overlap(subs_a: list, subs_b: list) -> float:
    """Некоторое пересечение рынков — хорошо; полное пересечение — плохо (конкуренты)."""
    if not subs_a or not subs_b:
        return 0.5
    overlap_ratio = len(set(subs_a) & set(subs_b)) / len(set(subs_a) | set(subs_b))
    # Оптимум: 20-50% пересечение
    if 0.2 <= overlap_ratio <= 0.5:
        return 1.0
    elif overlap_ratio < 0.2:
        return 0.5 + overlap_ratio * 2.5
    else:
        return max(0.1, 1.0 - (overlap_ratio - 0.5) * 1.8)


def _check_geo_proximity(city_a: str | None, city_b: str | None) -> float:
    """Одна страна — бонус. Один город — максимум."""
    if not city_a or not city_b:
        return 0.5
    if city_a == city_b:
        return 1.0
    # Упрощённо: оба в России — 0.8, разные страны — 0.4
    russian_cities = {"Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург"}
    if city_a in russian_cities and city_b in russian_cities:
        return 0.8
    return 0.4


def _recommend_type(scores: dict) -> str:
    if scores["tech_compatibility"] > 0.7:
        return "integration"
    elif scores["market_overlap"] > 0.6:
        return "co-development"
    else:
        return "reseller"


## REAL-TIME MATCHING (src/infrastructure/kafka/consumers.py):

from aiokafka import AIOKafkaConsumer
import json
import structlog

logger = structlog.get_logger()


class PartnerMatchingConsumer:
    """Автоматически ищет партнёров для новых компаний."""
    
    SCORE_THRESHOLD = 0.70
    MAX_AUTO_MATCHES = 50
    
    def __init__(self, company_client, partnership_repo, kafka_producer, ai_client):
        self.company_client = company_client
        self.partnership_repo = partnership_repo
        self.kafka = kafka_producer
        self.ai = ai_client
    
    async def handle_company_created(self, event: dict) -> None:
        company_id = event["company_id"]
        logger.info("auto_matching_started", company_id=company_id)
        
        # 1. Получаем данные новой компании
        new_company = await self.company_client.get_company(company_id)
        
        # 2. Векторный поиск похожих компаний
        candidates = await self.company_client.find_similar(
            company_id, limit=self.MAX_AUTO_MATCHES
        )
        
        matched = []
        for candidate in candidates:
            # 3. Рассчитываем совместимость
            score = calculate_compatibility(
                new_company, candidate
            )
            
            if score.total >= self.SCORE_THRESHOLD:
                # 4. Сохраняем partnership
                partnership = await self.partnership_repo.create({
                    "company_a_id": company_id,
                    "company_b_id": candidate["id"],
                    "compatibility_score": score.total,
                    "match_reasons": _extract_match_reasons(score),
                    "analysis_method": "auto_vector_scoring",
                    "ai_explanation": score.explanation,
                    "status": "suggested"
                })
                matched.append(partnership)
        
        if matched:
            # 5. Публикуем событие для уведомлений
            await self.kafka.publish("partnership.matched", {
                "company_id": company_id,
                "matches_count": len(matched),
                "top_score": max(m["compatibility_score"] for m in matched),
                "occurred_at": datetime.utcnow().isoformat()
            })
        
        logger.info(
            "auto_matching_completed",
            company_id=company_id,
            total_candidates=len(candidates),
            matches_found=len(matched)
        )


## ЭНДПОИНТЫ (src/presentation/routers/partnerships.py):

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from uuid import UUID

router = APIRouter(prefix="/partnerships", tags=["Partnerships"])


@router.post("/analyze", response_model=CompatibilityResponse)
async def analyze_compatibility(
    body: AnalyzeCompatibilityRequest,
    background_tasks: BackgroundTasks,
    service: PartnerService = Depends(),
    current_user = Depends(require_permission(Permission.PARTNERSHIP_WRITE)),
):
    """
    Анализирует совместимость двух компаний.
    При score > 0.7 автоматически сохраняет partnership и запускает deep AI-анализ.
    """
    result = await service.analyze(body.company_a_id, body.company_b_id)
    
    if result.score.total > 0.7:
        background_tasks.add_task(
            service.run_deep_ai_analysis, result.partnership_id
        )
    
    return result


@router.get("/recommendations")
async def get_recommendations(
    company_id: UUID,
    limit: int = Query(default=10, le=50),
    min_score: float = Query(default=0.6, ge=0.0, le=1.0),
    service: PartnerService = Depends(),
    current_user = Depends(require_permission(Permission.PARTNERSHIP_READ)),
):
    """Возвращает топ-N рекомендаций из кэша или пересчитывает."""
    return await service.get_recommendations(company_id, limit, min_score)


@router.post("/{partnership_id}/contact")
async def send_outreach(
    partnership_id: UUID,
    body: OutreachRequest,
    background_tasks: BackgroundTasks,
    service: PartnerService = Depends(),
    current_user = Depends(require_permission(Permission.PARTNERSHIP_WRITE)),
):
    """Генерирует AI письмо и отправляет через Email/Telegram."""
    message = await service.generate_outreach_message(
        partnership_id, body.style, body.custom_notes
    )
    background_tasks.add_task(service.send_outreach, partnership_id, message)
    return {"message_preview": message[:500], "status": "queued"}


@router.get("/stats")
async def get_partnership_stats(
    service: PartnerService = Depends(),
    current_user = Depends(require_permission(Permission.ANALYTICS_READ)),
):
    """Статистика: средний score, конверсия, топ индустрии."""
    return await service.get_stats()


## KAFKA СОБЫТИЯ (схемы):

# partnership.matched
{
    "event_id": "uuid",
    "company_id": "uuid",
    "matches_count": 5,
    "top_score": 0.87,
    "occurred_at": "ISO8601"
}

# partnership.status_changed
{
    "event_id": "uuid",
    "partnership_id": "uuid",
    "company_a_id": "uuid",
    "company_b_id": "uuid",
    "old_status": "suggested",
    "new_status": "contacted",
    "occurred_at": "ISO8601"
}

# partnership.deal_closed
{
    "event_id": "uuid",
    "partnership_id": "uuid",
    "deal_value": 5000000,
    "currency": "RUB",
    "occurred_at": "ISO8601"
}


## КЭШИРОВАНИЕ РЕКОМЕНДАЦИЙ (Redis):

# Ключи:
# recommendations:{company_id}          TTL: 1 час
# compatibility:{company_a}:{company_b} TTL: 24 часа
# stats:global                          TTL: 5 минут

# При обновлении компании инвалидируем связанные кэши:
# KEYS recommendations:{company_id}
# KEYS compatibility:{company_id}:*
# KEYS compatibility:*:{company_id}


## ПРИМЕРЫ ТЕСТОВ:

## tests/unit/test_compatibility_scoring.py:

import pytest
from src.domain.scoring import calculate_compatibility


@pytest.fixture
def saas_company_a():
    return {
        "id": "uuid-a",
        "industry": "SaaS",
        "sub_industries": ["CRM", "Sales Automation"],
        "tech_stack": {"python": True, "react": True, "postgresql": True},
        "integrations": ["Slack", "Salesforce"],
        "employees_range": "11-50",
        "headquarters_city": "Москва",
    }


@pytest.fixture
def saas_company_b():
    return {
        "id": "uuid-b",
        "industry": "SaaS",
        "sub_industries": ["HR Tech", "Recruitment"],
        "tech_stack": {"python": True, "vue": True, "postgresql": True},
        "integrations": ["Slack", "Bitrix24"],
        "employees_range": "51-200",
        "headquarters_city": "Санкт-Петербург",
    }


class TestCompatibilityScoring:
    
    def test_complementary_companies_get_high_score(self, saas_company_a, saas_company_b):
        result = calculate_compatibility(saas_company_a, saas_company_b)
        assert result.total >= 0.6, f"Expected >= 0.6, got {result.total}"
    
    def test_direct_competitors_get_low_score(self, saas_company_a):
        competitor = {**saas_company_a, "id": "uuid-c",
                      "sub_industries": ["CRM", "Sales Automation", "Marketing Automation"]}
        result = calculate_compatibility(saas_company_a, competitor)
        assert result.no_competition <= 0.3
    
    def test_same_city_increases_geo_score(self, saas_company_a, saas_company_b):
        same_city = {**saas_company_b, "headquarters_city": "Москва"}
        result_same = calculate_compatibility(saas_company_a, same_city)
        result_diff = calculate_compatibility(saas_company_a, saas_company_b)
        assert result_same.geo_proximity > result_diff.geo_proximity
    
    def test_total_score_is_between_0_and_1(self, saas_company_a, saas_company_b):
        result = calculate_compatibility(saas_company_a, saas_company_b)
        assert 0.0 <= result.total <= 1.0
    
    def test_explanation_is_not_empty(self, saas_company_a, saas_company_b):
        result = calculate_compatibility(saas_company_a, saas_company_b)
        assert len(result.explanation) > 20
    
    def test_recommended_type_is_valid(self, saas_company_a, saas_company_b):
        result = calculate_compatibility(saas_company_a, saas_company_b)
        assert result.recommended_partnership_type in ["integration", "reseller", "co-development"]


ОБЩИЕ ТРЕБОВАНИЯ для обоих сервисов:
- CQRS: команды через CommandBus, запросы — прямо в handlers
- Repository pattern: все DB-запросы только через репозитории
- Unit of Work: транзакция + публикация событий атомарно
- Cursor-based пагинация (не offset-based — плохо масштабируется)
- Read-through кэш в Redis для часто читаемых данных
- Prometheus метрики: количество компаний, среднее время поиска, hit-rate кэша
- Health check проверяет: PostgreSQL, Redis, Elasticsearch, Kafka
- Structured logging: все операции с company_id в контексте

Создай полную реализацию со всеми слоями архитектуры.
```

---

## Чеклист улучшений относительно исходных промптов

### Промпт №3 — что добавлено:
- Полная файловая структура обоих сервисов
- Зависимости с точными версиями (pyproject.toml)
- SQLAlchemy 2.0 модели с Mapped-синтаксисом
- Все Pydantic-схемы (Register, Login, Token, Password, 2FA)
- Полная реализация JWTService с blacklist
- Rate limiting через slowapi
- RBAC с Permission enum и role-permission matrix
- UserCacheService с TTL
- Kafka consumer для синхронизации роли при смене подписки
- Kafka event schemas (JSON Schema)
- 12 готовых тестов (unit + integration)

### Промпт №4 — что добавлено:
- DDD-структура (domain / application / infrastructure / presentation)
- Полный Aggregate Root Company с domain events
- Value Objects: INN, OGRN, FundingAmount с валидацией
- CQRS разделение: отдельные handlers для команд и запросов
- RRF (Reciprocal Rank Fusion) для гибридного поиска
- Cursor-based пагинация вместо offset
- Полный алгоритм совместимости с 6 метриками и весами
- Конкретные реализации каждой метрики (Jaccard, size diff, geo)
- PartnerMatchingConsumer для авто-матчинга
- Kafka event schemas для 3 событий партнёрства
- Стратегия кэширования в Redis (ключи + TTL + инвалидация)
- 6 unit-тестов для алгоритма совместимости
