"""Partner repository for partner service."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models.partner import Partnership, Company

class PartnerRepository:
    """Partner repository."""
    
    def __init__(self):
        pass
    
    async def get_by_id(self, db: AsyncSession, partnership_id: UUID) -> Optional[Partnership]:
        """Get partnership by ID (active only)."""
        stmt = select(Partnership).where(
            Partnership.id == partnership_id,
            Partnership.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_company(self, db: AsyncSession, company_id: UUID) -> List[Partnership]:
        """Get all partnerships for a company."""
        stmt = select(Partnership).where(
            Partnership.deleted_at.is_(None),
            (Partnership.company_id_1 == company_id) | (Partnership.company_id_2 == company_id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def create_partnership(self, db: AsyncSession, partnership_data: dict) -> Partnership:
        """Create new partnership."""
        partnership = Partnership(**partnership_data)
        db.add(partnership)
        await db.commit()
        await db.refresh(partnership)
        return partnership
    
    async def update_partnership(self, db: AsyncSession, partnership_id: UUID, update_data: dict) -> Partnership:
        """Update partnership."""
        stmt = (
            update(Partnership)
            .where(Partnership.id == partnership_id, Partnership.deleted_at.is_(None))
            .values(**update_data)
            .returning(Partnership)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    
    async def soft_delete_partnership(self, db: AsyncSession, partnership_id: UUID) -> None:
        """Soft delete partnership."""
        stmt = (
            update(Partnership)
            .where(Partnership.id == partnership_id)
            .values(deleted_at=datetime.utcnow())
        )
        await db.execute(stmt)
        await db.commit()
    
    async def get_company_by_id(self, db: AsyncSession, company_id: UUID) -> Optional[Company]:
        """Get company by ID (active only)."""
        stmt = select(Company).where(
            Company.id == company_id,
            Company.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def to_company_dict(self, company: Company) -> dict:
        """Convert company to dict."""
        return {
            "id": str(company.id),
            "name": company.name,
            "slug": company.slug,
            "description": company.description,
            "website": company.website,
            "industry": company.industry,
            "founded_year": company.founded_year,
            "headquarters_country": company.headquarters_country,
            "employees_count": company.employees_count,
            "created_at": company.created_at.isoformat(),
            "updated_at": company.updated_at.isoformat(),
        }