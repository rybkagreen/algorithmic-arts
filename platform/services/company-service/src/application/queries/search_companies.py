from typing import List, Optional

from .domain.company import Company
from .infrastructure.repositories.company_repository import CompanyRepository


class SearchCompaniesQuery:
    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    async def execute(
        self,
        name: Optional[str] = None,
        industry: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Company]:
        """Поиск компаний по имени и отрасли (только активные)."""
        companies_data = []
        
        if name and industry:
            # Поиск по имени и отрасли
            companies_data = await self.company_repository.search_by_name(name, skip=skip, limit=limit)
        elif name:
            # Поиск по имени
            companies_data = await self.company_repository.search_by_name(name, skip=skip, limit=limit)
        elif industry:
            # Поиск по отрасли
            companies_data = await self.company_repository.get_by_industry(industry, skip=skip, limit=limit)
        else:
            # Все активные компании
            companies_data = await self.company_repository.list_all(skip=skip, limit=limit)
        
        return [
            Company(**company.__dict__)
            for company in companies_data
        ]

    async def count_by_industry(self, industry: str) -> int:
        """Посчитать количество компаний в отрасли (только активные)."""
        return await self.company_repository.count_by_industry(industry)