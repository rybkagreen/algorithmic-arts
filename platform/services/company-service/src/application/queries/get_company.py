from uuid import UUID

from .domain.company import Company
from .domain.exceptions import CompanyNotFoundError
from .infrastructure.repositories.company_repository import CompanyRepository


class GetCompanyQuery:
    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    async def execute(self, company_id: UUID) -> Company:
        """Получить компанию по ID (только активные)."""
        company_data = await self.company_repository.get_by_id(company_id)
        if not company_data:
            raise CompanyNotFoundError(f"Company with id {company_id} not found or deleted")

        # Преобразование в доменный объект
        return Company(**company_data.__dict__)