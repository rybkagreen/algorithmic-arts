"""AI routers for AI core service."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.logging import get_logger
from .config import settings
from .core.exceptions import UserNotFoundError
from .dependencies import get_db, get_ai_service
from .schemas.ai import CompatibilityAnalysisRequest, CompatibilityAnalysisResponse, OutreachMessageRequest, OutreachMessageResponse

logger = get_logger("ai-router")

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/analyze-compatibility", response_model=CompatibilityAnalysisResponse)
async def analyze_compatibility(
    request: CompatibilityAnalysisRequest,
    ai_service = Depends(get_ai_service),
):
    """Analyze compatibility between two companies."""
    try:
        return await ai_service.analyze_compatibility(request)
    except Exception as e:
        logger.error("Compatibility analysis failed", error=str(e))
        raise HTTPException(status_code=400, detail="Compatibility analysis failed")


@router.post("/generate-outreach", response_model=OutreachMessageResponse)
async def generate_outreach_message(
    request: OutreachMessageRequest,
    ai_service = Depends(get_ai_service),
):
    """Generate personalized outreach message."""
    try:
        return await ai_service.generate_outreach_message(request)
    except Exception as e:
        logger.error("Outreach message generation failed", error=str(e))
        raise HTTPException(status_code=400, detail="Outreach message generation failed")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-core-service"}