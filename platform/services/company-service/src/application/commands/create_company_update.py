from typing import Dict, List
from uuid import UUID

from .infrastructure.repositories.company_update_repository import CompanyUpdateRepository
from .infrastructure.repositories.company_repository import CompanyRepository


class CreateCompanyUpdateCommand:
    def __init__(
        self,
        company_repo: CompanyRepository,
        update_repo: CompanyUpdateRepository
    ):
        self.company_repo = company_repo
        self.update_repo = update_repo

    async def execute(
        self,
        company_id: UUID,
        update_type: str,
        old_data: Dict,
        new_data: Dict,
        changed_fields: List[str]
    ) -> UUID:
        """Создать запись об обновлении компании."""
        # Проверяем, что компания существует и активна
        company = await self.company_repo.get_by_id(company_id)
        if not company:
            raise Exception(f"Company with id {company_id} not found or deleted")

        # Создаем запись об обновлении
        update_record = await self.update_repo.create_update(
            company_id=company_id,
            update_type=update_type,
            old_value=old_data,
            new_value=new_data,
            changed_fields=changed_fields
        )

        return update_record.id