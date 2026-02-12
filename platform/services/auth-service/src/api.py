from typing import Dict

from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/ping", response_model=Dict[str, str])
async def ping() -> Dict[str, str]:
    return {"message": "Auth Service is running"}
