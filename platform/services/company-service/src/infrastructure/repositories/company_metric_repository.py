from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from .base_repository import BaseRepository
from ..models import CompanyMetric


class CompanyMetricRepository(BaseRepository[CompanyMetric]):
    """Репозиторий для работы с метриками компаний (partitioned table)."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, CompanyMetric)
    
    async def create_metric(
        self,
        company_id: UUID,
        metric_type: str,
        value: float,
        unit: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> CompanyMetric:
        """Создать запись о метрике компании."""
        if not period_start:
            period_start = datetime.utcnow()
        if not period_end:
            period_end = datetime.utcnow()
        
        stmt = insert(CompanyMetric).values(
            company_id=company_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            period_start=period_start,
            period_end=period_end,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ).returning(CompanyMetric)
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()
    
    async def get_metrics_by_company(
        self,
        company_id: UUID,
        metric_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyMetric]:
        """Получить метрики компании."""
        stmt = select(CompanyMetric).where(
            CompanyMetric.company_id == company_id
        )
        
        if metric_type:
            stmt = stmt.where(CompanyMetric.metric_type == metric_type)
        if start_date:
            stmt = stmt.where(CompanyMetric.period_start >= start_date)
        if end_date:
            stmt = stmt.where(CompanyMetric.period_end <= end_date)
        
        stmt = stmt.order_by(CompanyMetric.period_start.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_latest_metric(
        self,
        company_id: UUID,
        metric_type: str
    ) -> Optional[CompanyMetric]:
        """Получить последнюю метрику компании по типу."""
        stmt = select(CompanyMetric).where(
            CompanyMetric.company_id == company_id,
            CompanyMetric.metric_type == metric_type
        ).order_by(CompanyMetric.period_start.desc()).limit(1)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def count_metrics_by_company(self, company_id: UUID) -> int:
        """Посчитать количество метрик компании."""
        stmt = select(self.model_class).where(
            CompanyMetric.company_id == company_id
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())