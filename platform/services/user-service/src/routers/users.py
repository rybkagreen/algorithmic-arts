"""User routers for user service."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.logging import get_logger
from .config import settings
from .core.exceptions import UserNotFoundError
from .dependencies import get_db, get_user_service
from .schemas.user import UserCreate, UserUpdate, UserOut, CompanyCreate, CompanyUpdate, CompanyOut

logger = get_logger("user-router")

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    body: UserCreate,
    user_service = Depends(get_user_service),
):
    """Register new user."""
    try:
        return await user_service.create_user(body)
    except Exception as e:
        logger.error("User registration failed", error=str(e))
        raise HTTPException(status_code=400, detail="User registration failed")


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: str,
    user_service = Depends(get_user_service),
):
    """Get user by ID."""
    try:
        return await user_service.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    body: UserUpdate,
    user_service = Depends(get_user_service),
):
    """Update user."""
    try:
        return await user_service.update_user(user_id, body)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    user_service = Depends(get_user_service),
):
    """Delete user (soft delete)."""
    try:
        await user_service.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/companies", status_code=status.HTTP_201_CREATED)
async def create_company(
    body: CompanyCreate,
    user_service = Depends(get_user_service),
):
    """Create new company."""
    try:
        return await user_service.create_company(body)
    except Exception as e:
        logger.error("Company creation failed", error=str(e))
        raise HTTPException(status_code=400, detail="Company creation failed")


@router.get("/companies/{company_id}", response_model=CompanyOut)
async def get_company(
    company_id: str,
    user_service = Depends(get_user_service),
):
    """Get company by ID."""
    try:
        return await user_service.get_company_by_id(company_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/companies/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: str,
    body: CompanyUpdate,
    user_service = Depends(get_user_service),
):
    """Update company."""
    try:
        return await user_service.update_company(company_id, body)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/companies/{company_id}/users", response_model=list[UserOut])
async def get_users_for_company(
    company_id: str,
    user_service = Depends(get_user_service),
):
    """Get all users for a company."""
    try:
        return await user_service.get_users_for_company(company_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/assign/{user_id}/to/{company_id}", response_model=UserOut)
async def assign_user_to_company(
    user_id: str,
    company_id: str,
    user_service = Depends(get_user_service),
):
    """Assign user to company."""
    try:
        return await user_service.assign_user_to_company(user_id, company_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "user-service"}