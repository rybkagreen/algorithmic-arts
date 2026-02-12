from typing import Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models.user_profile import UserProfile


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user_id: str) -> Optional[UserProfile]:
        stmt = select(UserProfile).where(UserProfile.user_id == user_id, UserProfile.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_profile(self, profile: UserProfile) -> UserProfile:
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update_profile(self, profile: UserProfile) -> UserProfile:
        await self.db.commit()
        await self.db.refresh(profile)
        return profile