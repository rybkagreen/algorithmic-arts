from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .core.permissions import require_permission
from .dependencies import get_cache_service, get_db, get_user_repository
from .schemas.user import UserProfileCreate, UserProfileUpdate
from .services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile")
async def get_user_profile(
    user_id: str,
    service: UserService = Depends(),
):
    return await service.get_profile(user_id)


@router.post("/profile")
async def create_user_profile(
    user_id: str,
    data: UserProfileCreate,
    service: UserService = Depends(),
):
    return await service.create_profile(user_id, data)


@router.put("/profile")
async def update_user_profile(
    user_id: str,
    data: UserProfileUpdate,
    service: UserService = Depends(),
):
    return await service.update_profile(user_id, data)