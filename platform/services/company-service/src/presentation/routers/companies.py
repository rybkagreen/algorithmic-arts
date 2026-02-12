from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .application.commands.create_company import CreateCompanyCommand
from .application.queries.get_company import GetCompanyQuery
from .config import settings
from .dependencies import get_db
from .infrastructure.kafka.producers import CompanyEventProducer
from .infrastructure.repositories.company_repository import CompanyRepository
from .schemas.company import CompanyCreate, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
):
    # В реальной реализации здесь будет DI через FastAPI dependencies
    company_repo = CompanyRepository(db)
    event_producer = CompanyEventProducer(settings.kafka.bootstrap_servers)
    
    command = CreateCompanyCommand(company_repo, event_producer)
    company = await command.execute(**data.dict())
    
    return {"id": str(company.id), "name": company.name}


@router.get("/{company_id}")
async def get_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    company_repo = CompanyRepository(db)
    query = GetCompanyQuery(company_repo)
    company = await query.execute(company_id)
    
    return company.to_dict()