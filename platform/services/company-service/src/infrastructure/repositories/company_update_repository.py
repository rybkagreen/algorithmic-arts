from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from .base_repository import BaseRepository
from ..models import CompanyUpdate


class CompanyUpdateRepository(BaseRepository[CompanyUpdate]):
    """Репозиторий для работы с обновлениями компаний (partitioned table)."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, CompanyUpdate)
    
    async def create_update(
        self,
        company_id: UUID,
        update_type: str,
        old_value: dict,
        new_value: dict,
        changed_fields: List[str]
    ) -> CompanyUpdate:
        """Создать запись об обновлении компании."""
        stmt = insert(CompanyUpdate).values(
            company_id=company_id,
            update_type=update_type,
            old_value=old_value,
            new_value=new_value,
            changed_fields=changed_fields,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ).returning(CompanyUpdate)
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()
    
    async def get_updates_by_company(
        self,
        company_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyUpdate]:
        """Получить обновления компании за период."""
        stmt = select(CompanyUpdate).where(
            CompanyUpdate.company_id == company_id
        )
        
        if start_date:
            stmt = stmt.where(CompanyUpdate.created_at >= start_date)
        if end_date:
            stmt = stmt.where(CompanyUpdate.created_at <= end_date)
        
        stmt = stmt.order_by(CompanyUpdate.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count_updates_by_company(self, company_id: UUID) -> int:
        """Посчитать количество обновлений компании."""
        stmt = select(self.model_class).where(
            CompanyUpdate.company_id == company_id
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())