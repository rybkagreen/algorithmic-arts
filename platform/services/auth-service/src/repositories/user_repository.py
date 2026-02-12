from typing import Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def increment_failed_login_count(self, user_id: str) -> None:
        if user_id:
            stmt = update(User).where(User.id == user_id).values(
                failed_login_count=User.failed_login_count + 1
            )
            await self.db.execute(stmt)
            await self.db.commit()

    async def reset_failed_login_count(self, user_id: str) -> None:
        if user_id:
            stmt = update(User).where(User.id == user_id).values(failed_login_count=0)
            await self.db.execute(stmt)
            await self.db.commit()

    async def delete(self, user_id: str) -> None:
        stmt = update(User).where(User.id == user_id).values(deleted_at=datetime.utcnow())
        await self.db.execute(stmt)
        await self.db.commit()