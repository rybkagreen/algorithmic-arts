from typing import List

from .domain.company import Company
from .infrastructure.repositories.company_repository import CompanyRepository


class ListCompaniesQuery:
    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """Получить список активных компаний."""
        companies_data = await self.company_repository.list_all(skip=skip, limit=limit)
        
        return [
            Company(**company.__dict__)
            for company in companies_data
        ]

    async def count_active(self) -> int:
        """Посчитать количество активных компаний."""
        return await self.company_repository.get_active_companies_count()