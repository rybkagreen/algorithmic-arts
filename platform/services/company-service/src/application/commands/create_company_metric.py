from datetime import datetime
from typing import Optional
from uuid import UUID

from .infrastructure.repositories.company_metric_repository import CompanyMetricRepository
from .infrastructure.repositories.company_repository import CompanyRepository


class CreateCompanyMetricCommand:
    def __init__(
        self,
        company_repo: CompanyRepository,
        metric_repo: CompanyMetricRepository
    ):
        self.company_repo = company_repo
        self.metric_repo = metric_repo

    async def execute(
        self,
        company_id: UUID,
        metric_type: str,
        value: float,
        unit: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> UUID:
        """Создать запись о метрике компании."""
        # Проверяем, что компания существует и активна
        company = await self.company_repo.get_by_id(company_id)
        if not company:
            raise Exception(f"Company with id {company_id} not found or deleted")

        # Создаем запись о метрике
        metric_record = await self.metric_repo.create_metric(
            company_id=company_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            period_start=period_start,
            period_end=period_end
        )

        return metric_record.id