"""AI repository for AI core service."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models.ai import AIAnalysis, OutreachMessage

class AIRepository:
    """AI repository."""
    
    def __init__(self):
        pass
    
    async def save_compatibility_analysis(self, db: AsyncSession, analysis_data: dict) -> AIAnalysis:
        """Save compatibility analysis."""
        analysis = AIAnalysis(**analysis_data)
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        return analysis
    
    async def get_compatibility_analysis(self, db: AsyncSession, analysis_id: UUID) -> Optional[AIAnalysis]:
        """Get compatibility analysis by ID."""
        stmt = select(AIAnalysis).where(
            AIAnalysis.id == analysis_id,
            AIAnalysis.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def save_outreach_message(self, db: AsyncSession, message_data: dict) -> OutreachMessage:
        """Save outreach message."""
        message = OutreachMessage(**message_data)
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message
    
    async def get_outreach_message(self, db: AsyncSession, message_id: UUID) -> Optional[OutreachMessage]:
        """Get outreach message by ID."""
        stmt = select(OutreachMessage).where(
            OutreachMessage.id == message_id,
            OutreachMessage.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()