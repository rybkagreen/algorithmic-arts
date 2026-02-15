from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from shared.logging import get_logger

logger = get_logger()

from .application.commands.create_company import CreateCompanyCommand
from .application.commands.update_company import UpdateCompanyCommand
from .application.commands.delete_company import DeleteCompanyCommand
from .application.queries.get_company import GetCompanyQuery
from .application.queries.list_companies import ListCompaniesQuery
from .application.queries.search_companies import SearchCompaniesQuery
from .application.queries.get_similar_companies import GetSimilarCompaniesQuery
from .dependencies import get_db, get_company_repository, get_company_indexer
from .infrastructure.repositories.company_repository import CompanyRepository
from .schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from .domain.exceptions import CompanyNotFoundError

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("", status_code=status.HTTP_201_CREATED, operation_id="createCompany")
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    company_repo: CompanyRepository = Depends(get_company_repository),
):
    """Создать новую компанию."""
    try:
        command = CreateCompanyCommand(
            name=data.name,
            slug=data.slug,
            description=data.description,
            website=data.website,
            industry=data.industry,
            sub_industries=data.sub_industries,
            business_model=data.business_model,
            founded_year=data.founded_year,
            headquarters_country=data.headquarters_country,
            headquarters_city=data.headquarters_city,
            employees_count=data.employees_count,
            employees_range=data.employees_range,
            funding_stage=data.funding_stage,
            legal_name=data.legal_name,
            tech_stack=data.tech_stack,
            integrations=data.integrations,
            api_available=data.api_available,
            is_verified=data.is_verified
        )

        company_id = await command.execute(db, company_repo)
        return {"id": str(company_id), "message": "Company created successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{company_id}", response_model=CompanyResponse, operation_id="getCompany")
async def get_company(
    company_id: UUID,
    company_repo: CompanyRepository = Depends(get_company_repository),
    get_company_query: GetCompanyQuery = Depends(),
):
    """Получить компанию по ID (только активные)."""
    try:
        company = await get_company_query.execute(company_id)
        return company
    except CompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=List[CompanyResponse], operation_id="listCompanies")
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    company_repo: CompanyRepository = Depends(get_company_repository),
    list_companies_query: ListCompaniesQuery = Depends(),
):
    """Получить список активных компаний."""
    companies = await list_companies_query.execute(skip=skip, limit=limit)
    return companies


@router.get("/search", response_model=List[CompanyResponse], operation_id="searchCompanies")
async def search_companies(
    name: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    company_repo: CompanyRepository = Depends(get_company_repository),
    search_query: SearchCompaniesQuery = Depends(),
):
    """Поиск компаний по имени и отрасли (только активные)."""
    companies = await search_query.execute(
        name=name,
        industry=industry,
        skip=skip,
        limit=limit
    )
    return companies


@router.put("/{company_id}", response_model=CompanyResponse, operation_id="updateCompany")
async def update_company(
    company_id: UUID,
    data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    company_repo: CompanyRepository = Depends(get_company_repository),
):
    """Обновить компанию (только активные)."""
    try:
        command = UpdateCompanyCommand(
            company_id=company_id,
            name=data.name,
            description=data.description,
            website=data.website,
            industry=data.industry,
            sub_industries=data.sub_industries,
            business_model=data.business_model,
            founded_year=data.founded_year,
            headquarters_country=data.headquarters_country,
            headquarters_city=data.headquarters_city,
            employees_count=data.employees_count,
            employees_range=data.employees_range,
            funding_stage=data.funding_stage,
            legal_name=data.legal_name,
            tech_stack=data.tech_stack,
            integrations=data.integrations,
            api_available=data.api_available,
            is_verified=data.is_verified
        )

        updated_company = await command.execute(db, company_repo)
        return updated_company
    except CompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteCompany")
async def delete_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    company_repo: CompanyRepository = Depends(get_company_repository),
):
    """Мягкое удаление компании."""
    try:
        command = DeleteCompanyCommand(company_id=company_id)
        success = await command.execute(db, company_repo)
        if not success:
            raise CompanyNotFoundError(f"Company with id {company_id} not found or already deleted")
    except CompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{company_id}/similar", response_model=List[CompanyResponse], operation_id="getSimilarCompanies")
async def get_similar_companies(
    company_id: UUID,
    top_k: int = Query(5, ge=1, le=20),
    company_repo: CompanyRepository = Depends(get_company_repository),
    indexer: CompanyIndexer = Depends(get_company_indexer),
    similar_query: GetSimilarCompaniesQuery = Depends(),
):
    """Получить похожие компании (только активные)."""
    try:
        companies = await similar_query.execute(company_id=company_id, top_k=top_k)
        return companies
    except Exception as exc:
        logger.error("Failed to get similar companies", error=str(exc), company_id=company_id)
        raise


