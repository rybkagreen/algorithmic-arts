"""Partner routers for partner service."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.logging import get_logger
from .config import settings
from .core.exceptions import UserNotFoundError
from .dependencies import get_db, get_partner_service
from .schemas.partner import PartnershipCreate, PartnershipUpdate, PartnershipOut

logger = get_logger("partner-router")

router = APIRouter(prefix="/partnerships", tags=["Partnerships"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_partnership(
    body: PartnershipCreate,
    partner_service = Depends(get_partner_service),
):
    """Create new partnership."""
    try:
        return await partner_service.create_partnership(body)
    except Exception as e:
        logger.error("Partnership creation failed", error=str(e))
        raise HTTPException(status_code=400, detail="Partnership creation failed")


@router.get("/{partnership_id}", response_model=PartnershipOut)
async def get_partnership(
    partnership_id: str,
    partner_service = Depends(get_partner_service),
):
    """Get partnership by ID."""
    try:
        return await partner_service.get_partnership_by_id(partnership_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{partnership_id}", response_model=PartnershipOut)
async def update_partnership(
    partnership_id: str,
    body: PartnershipUpdate,
    partner_service = Depends(get_partner_service),
):
    """Update partnership."""
    try:
        return await partner_service.update_partnership(partnership_id, body)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/company/{company_id}", response_model=list[PartnershipOut])
async def get_partnerships_for_company(
    company_id: str,
    partner_service = Depends(get_partner_service),
):
    """Get all partnerships for a company."""
    try:
        return await partner_service.get_partnerships_for_company(company_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{partnership_id}")
async def delete_partnership(
    partnership_id: str,
    partner_service = Depends(get_partner_service),
):
    """Delete partnership (soft delete)."""
    try:
        await partner_service.delete_partnership(partnership_id)
        return {"message": "Partnership deleted successfully"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "partner-service"}