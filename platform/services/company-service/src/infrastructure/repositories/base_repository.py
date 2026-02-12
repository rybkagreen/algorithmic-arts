from typing import TypeVar, Generic, Optional, List, Type
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Базовый репозиторий с поддержкой soft delete."""
    
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
    
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Получить запись по ID (только активные)."""
        stmt = select(self.model_class).where(
            self.model_class.id == id,
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Получить список всех активных записей."""
        stmt = select(self.model_class).where(
            self.model_class.deleted_at.is_(None)
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count_active(self) -> int:
        """Посчитать количество активных записей."""
        stmt = select(self.model_class).where(
            self.model_class.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
    
    async def soft_delete(self, id: UUID) -> bool:
        """Мягкое удаление записи."""
        stmt = update(self.model_class).where(
            self.model_class.id == id,
            self.model_class.deleted_at.is_(None)
        ).values(deleted_at=datetime.utcnow())
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def hard_delete(self, id: UUID) -> bool:
        """Жесткое удаление записи."""
        stmt = delete(self.model_class).where(self.model_class.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def restore(self, id: UUID) -> bool:
        """Восстановление мягко удаленной записи."""
        stmt = update(self.model_class).where(
            self.model_class.id == id,
            self.model_class.deleted_at.is_not(None)
        ).values(deleted_at=None)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0