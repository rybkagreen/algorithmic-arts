from typing import Dict, Any
from uuid import UUID
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from ...models.partnership import PartnershipORM


async def save_partnership_suggestion(
    company_a_id: UUID,
    company_b_id: UUID,
    score: float,
    report: Dict[str, Any],
    session: AsyncSession
) -> UUID:
    """Сохранить предложенное партнёрство."""
    # Гарантируем a < b для UNIQUE constraint
    a, b = sorted([company_a_id, company_b_id])
    stmt = pg_insert(PartnershipORM).values(
        id=UUID(int=0),  # будет сгенерировано
        company_a_id=a,
        company_b_id=b,
        compatibility_score=score,
        ai_explanation=report.get("pitch_angle"),
        recommended_type=report.get("recommended_type"),
        status="suggested",
        analysis_method="ai_deep_analysis",
    ).on_conflict_do_nothing()
    
    result = await session.execute(stmt)
    await session.commit()
    
    # Получаем ID вставленной записи
    if result.inserted_primary_key:
        return result.inserted_primary_key[0]
    else:
        # Если запись уже существует (on_conflict_do_nothing), получаем существующий ID
        result = await session.execute(
            select(PartnershipORM.id)
            .where(PartnershipORM.company_a_id == a, PartnershipORM.company_b_id == b)
        )
        existing_id = result.scalar_one_or_none()
        return existing_id or UUID(int=0)


async def update_company_enrichment(
    company_id: UUID,
    enrichment: Dict[str, Any],
    session: AsyncSession
) -> None:
    """Обновить поля обогащения компании."""
    await session.execute(
        text("""
            UPDATE companies 
            SET 
                ai_summary = :ai_summary,
                ai_tags = :ai_tags,
                updated_at = NOW()
            WHERE id = :company_id
        """),
        {
            "company_id": str(company_id),
            "ai_summary": enrichment.get("ai_summary"),
            "ai_tags": enrichment.get("ai_tags", [])
        }
    )
    await session.commit()