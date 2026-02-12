from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .core.cache import UserCacheService
from .core.permissions import require_permission
from .models.user_profile import UserProfile
from .repositories.user_repository import UserRepository
from .schemas.user import UserProfileCreate, UserProfileUpdate


class UserService:
    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepository,
        cache_service: UserCacheService,
    ):
        self.db = db
        self.user_repository = user_repository
        self.cache_service = cache_service

    async def get_profile(self, user_id: UUID) -> dict:
        # Попытка получить из кэша
        cached = await self.cache_service.get(user_id)
        if cached:
            return cached

        # Получение из БД
        profile = await self.user_repository.get_profile(user_id)
        if not profile:
            return {}

        # Кэширование
        await self.cache_service.set(user_id, profile.__dict__)
        return profile.__dict__

    async def create_profile(self, user_id: UUID, data: UserProfileCreate) -> UserProfile:
        profile = UserProfile(
            user_id=user_id,
            avatar_url=data.avatar_url,
            bio=data.bio,
            job_title=data.job_title,
            location=data.location,
            timezone=data.timezone,
            language=data.language,
            theme_preference=data.theme_preference or "light",
            email_notifications=data.email_notifications if data.email_notifications is not None else True,
            push_notifications=data.push_notifications if data.push_notifications is not None else True,
            sms_notifications=data.sms_notifications if data.sms_notifications is not None else False,
            two_factor_method=data.two_factor_method,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return await self.user_repository.create_profile(profile)

    async def update_profile(self, user_id: UUID, data: UserProfileUpdate) -> UserProfile:
        profile = await self.user_repository.get_profile(user_id)
        if not profile:
            raise ValueError("Profile not found")

        # Обновление полей
        for field, value in data.dict(exclude_unset=True).items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        updated_profile = await self.user_repository.update_profile(profile)
        
        # Инвалидация кэша
        await self.cache_service.invalidate(user_id)
        
        return updated_profile