from typing import List, Dict, Optional, Any
from uuid import UUID
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ...models.company import CompanyORM


async def get_company(company_id: UUID, session: AsyncSession) -> Optional[Dict[str, Any]]:
    """Получить компанию из БД по ID."""
    result = await session.execute(
        select(CompanyORM)
        .where(CompanyORM.id == company_id, CompanyORM.deleted_at.is_(None))
        .options(selectinload(CompanyORM.metrics), selectinload(CompanyORM.updates))
    )
    row = result.scalar_one_or_none()
    if row:
        return row.__dict__
    return None


async def search_similar_companies(
    embedding: List[float],
    limit: int = 20,
    threshold: float = 0.7,
    session: AsyncSession = None
) -> List[Dict[str, Any]]:
    """Векторный поиск похожих компаний."""
    if not session:
        raise ValueError("session required")
        
    result = await session.execute(text("""
        SELECT id, name, industry, sub_industries, tech_stack,
               1 - (embedding <=> :emb::vector) AS similarity
        FROM companies
        WHERE deleted_at IS NULL AND embedding IS NOT NULL
          AND 1 - (embedding <=> :emb::vector) >= :threshold
        ORDER BY embedding <=> :emb::vector
        LIMIT :limit
    """), {"emb": str(embedding), "threshold": threshold, "limit": limit})
    return [dict(r._mapping) for r in result.fetchall()]