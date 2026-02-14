"""User repository for user service."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models.user import User, Company

class UserRepository:
    """User repository."""
    
    def __init__(self):
        pass
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email (active only)."""
        stmt = select(User).where(
            User.email == email,
            User.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get user by ID (active only)."""
        stmt = select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_user(self, db: AsyncSession, user_data: dict) -> User:
        """Create new user."""
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def update_user(self, db: AsyncSession, user_id: UUID, update_data: dict) -> User:
        """Update user."""
        stmt = (
            update(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
            .values(**update_data)
            .returning(User)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    
    async def soft_delete_user(self, db: AsyncSession, user_id: UUID) -> None:
        """Soft delete user."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(deleted_at=datetime.utcnow())
        )
        await db.execute(stmt)
        await db.commit()
    
    async def create_company(self, db: AsyncSession, company_data: dict) -> Company:
        """Create new company."""
        company = Company(**company_data)
        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company
    
    async def get_company_by_id(self, db: AsyncSession, company_id: UUID) -> Optional[Company]:
        """Get company by ID (active only)."""
        stmt = select(Company).where(
            Company.id == company_id,
            Company.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_company_by_slug(self, db: AsyncSession, slug: str) -> Optional[Company]:
        """Get company by slug (active only)."""
        stmt = select(Company).where(
            Company.slug == slug,
            Company.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_company(self, db: AsyncSession, company_id: UUID, update_data: dict) -> Company:
        """Update company."""
        stmt = (
            update(Company)
            .where(Company.id == company_id, Company.deleted_at.is_(None))
            .values(**update_data)
            .returning(Company)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    
    async def get_users_by_company(self, db: AsyncSession, company_id: UUID) -> List[User]:
        """Get all users for a company."""
        stmt = select(User).where(
            User.company_id == company_id,
            User.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def to_dict(self, user: User) -> dict:
        """Convert user to dict."""
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }
    
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