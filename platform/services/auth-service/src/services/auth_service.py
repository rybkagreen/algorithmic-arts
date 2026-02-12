from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    PasswordTooWeakError,
)
from .core.security import get_password_hash, verify_password
from .models.user import User
from .repositories.user_repository import UserRepository
from .schemas.auth import LoginRequest, RegisterRequest
from .services.jwt_service import JWTService


class AuthService:
    def __init__(
        self,
        db: AsyncSession,
        jwt_service: JWTService,
        user_repository: UserRepository,
    ):
        self.db = db
        self.jwt_service = jwt_service
        self.user_repository = user_repository

    async def register(self, data: RegisterRequest) -> User:
        # Проверка на существование email
        existing_user = await self.user_repository.get_by_email(data.email)
        if existing_user:
            raise EmailAlreadyExistsError()

        # Хеширование пароля
        hashed_password = get_password_hash(data.password)

        # Создание пользователя
        user = User(
            email=data.email,
            password_hash=hashed_password,
            full_name=data.full_name,
            company_name=data.company_name,
            role="free_user",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return await self.user_repository.create(user)

    async def authenticate(self, data: LoginRequest) -> dict:
        user = await self.user_repository.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            # Увеличиваем счетчик неудачных попыток
            await self.user_repository.increment_failed_login_count(user.id if user else None)
            raise InvalidCredentialsError()

        # Сброс счетчика неудачных попыток при успешной авторизации
        await self.user_repository.reset_failed_login_count(user.id)

        # Обновляем время последнего входа
        user.last_login_at = datetime.utcnow()
        await self.user_repository.update(user)

        # Создаем токены
        access_token = await self.jwt_service.create_access_token(user.id, user.role.value)
        refresh_token = await self.jwt_service.create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,
        }

    async def refresh_tokens(self, refresh_token: str) -> dict:
        try:
            payload = await self.jwt_service.verify_token(refresh_token)
            user_id = UUID(payload["sub"])
            
            # Проверяем, что это refresh token
            if payload.get("type") != "refresh":
                raise InvalidCredentialsError("Недопустимый тип токена")

            # Создаем новый access token
            user = await self.user_repository.get(user_id)
            if not user:
                raise InvalidCredentialsError("Пользователь не найден")

            access_token = await self.jwt_service.create_access_token(user.id, user.role.value)
            new_refresh_token = await self.jwt_service.create_refresh_token(user.id)

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": 900,
            }
        except Exception:
            raise InvalidCredentialsError("Неверный refresh token")