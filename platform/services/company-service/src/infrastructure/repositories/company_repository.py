from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from .base_repository import BaseRepository
from ..models import Company as CompanyModel
from ..domain.company import Company


class CompanyRepository(BaseRepository[CompanyModel]):
    """Репозиторий для работы с компаниями с поддержкой soft delete."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, CompanyModel)
    
    async def get_by_slug(self, slug: str) -> Optional[CompanyModel]:
        """Получить компанию по slug (только активные)."""
        stmt = select(CompanyModel).where(
            CompanyModel.slug == slug,
            CompanyModel.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[CompanyModel]:
        """Поиск компаний по имени (только активные)."""
        stmt = select(CompanyModel).where(
            CompanyModel.name.ilike(f"%{name}%"),
            CompanyModel.deleted_at.is_(None)
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_industry(self, industry: str, skip: int = 0, limit: int = 100) -> List[CompanyModel]:
        """Получить компании по отрасли (только активные)."""
        stmt = select(CompanyModel).where(
            CompanyModel.industry == industry,
            CompanyModel.deleted_at.is_(None)
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count_by_industry(self, industry: str) -> int:
        """Посчитать количество компаний в отрасли (только активные)."""
        stmt = select(func.count()).select_from(CompanyModel).where(
            CompanyModel.industry == industry,
            CompanyModel.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def create_from_domain(self, company: Company) -> CompanyModel:
        """Создать компанию из domain объекта."""
        db_company = CompanyModel(
            id=company.id,
            name=company.name,
            slug=company.slug,
            description=company.description,
            website=company.website,
            industry=company.industry,
            sub_industries=company.sub_industries,
            business_model=company.business_model,
            founded_year=company.founded_year,
            headquarters_country=company.headquarters_country,
            headquarters_city=company.headquarters_city,
            employees_count=company.employees_count,
            employees_range=company.employees_range,
            funding_total_amount=company.funding_total.amount if company.funding_total else None,
            funding_total_currency=company.funding_total.currency if company.funding_total else None,
            funding_stage=company.funding_stage,
            last_funding_date=company.last_funding_date,
            inn=company.inn.value if company.inn else None,
            ogrn=company.ogrn.value if company.ogrn else None,
            legal_name=company.legal_name,
            tech_stack=company.tech_stack,
            integrations=company.integrations,
            api_available=company.api_available,
            ai_summary=company.ai_summary,
            ai_tags=company.ai_tags,
            embedding=company.embedding,
            is_verified=company.is_verified,
            view_count=company.view_count,
            created_at=company.created_at,
            updated_at=company.updated_at,
            deleted_at=company.deleted_at
        )
        self.session.add(db_company)
        await self.session.commit()
        await self.session.refresh(db_company)
        return db_company
    
    async def update_from_domain(self, company_id: UUID, company: Company) -> CompanyModel:
        """Обновить компанию из domain объекта."""
        stmt = update(CompanyModel).where(
            CompanyModel.id == company_id,
            CompanyModel.deleted_at.is_(None)
        ).values(
            name=company.name,
            slug=company.slug,
            description=company.description,
            website=company.website,
            industry=company.industry,
            sub_industries=company.sub_industries,
            business_model=company.business_model,
            founded_year=company.founded_year,
            headquarters_country=company.headquarters_country,
            headquarters_city=company.headquarters_city,
            employees_count=company.employees_count,
            employees_range=company.employees_range,
            funding_total_amount=company.funding_total.amount if company.funding_total else None,
            funding_total_currency=company.funding_total.currency if company.funding_total else None,
            funding_stage=company.funding_stage,
            last_funding_date=company.last_funding_date,
            inn=company.inn.value if company.inn else None,
            ogrn=company.ogrn.value if company.ogrn else None,
            legal_name=company.legal_name,
            tech_stack=company.tech_stack,
            integrations=company.integrations,
            api_available=company.api_available,
            ai_summary=company.ai_summary,
            ai_tags=company.ai_tags,
            embedding=company.embedding,
            is_verified=company.is_verified,
            view_count=company.view_count,
            updated_at=company.updated_at
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        # Получаем обновленную запись
        stmt = select(CompanyModel).where(CompanyModel.id == company_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_active_companies_count(self) -> int:
        """Получить количество активных компаний."""
        stmt = select(func.count()).select_from(CompanyModel).where(
            CompanyModel.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0