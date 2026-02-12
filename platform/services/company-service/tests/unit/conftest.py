import pytest
from unittest.mock import AsyncMock
from src.infrastructure.repositories.company_repository import CompanyRepository
from src.infrastructure.elasticsearch.company_indexer import CompanyIndexer
from src.domain.company import Company
from uuid import uuid4
from datetime import datetime


@pytest.fixture
def mock_company_repo():
    """Мок репозитория компании для unit тестов."""
    mock = AsyncMock(spec=CompanyRepository)
    
    # Настройка стандартных моков
    mock.get_by_id = AsyncMock(return_value=None)
    mock.list_all = AsyncMock(return_value=[])
    mock.search_by_name = AsyncMock(return_value=[])
    mock.get_by_industry = AsyncMock(return_value=[])
    mock.create_from_domain = AsyncMock(return_value=None)
    mock.update_from_domain = AsyncMock(return_value=None)
    mock.soft_delete = AsyncMock(return_value=True)
    mock.get_active_companies_count = AsyncMock(return_value=0)
    mock.count_by_industry = AsyncMock(return_value=0)
    
    return mock


@pytest.fixture
def mock_company_indexer():
    """Мок индексера для unit тестов."""
    mock = AsyncMock(spec=CompanyIndexer)
    mock.index_company = AsyncMock(return_value=None)
    mock.search_companies = AsyncMock(return_value={"hits": {"total": {"value": 0}, "hits": []}})
    mock.get_similar_companies = AsyncMock(return_value={"hits": {"total": {"value": 0}, "hits": []}})
    return mock


@pytest.fixture
def sample_company():
    """Пример компании для тестов."""
    return Company(
        id=uuid4(),
        name="Test Company",
        slug="test-company",
        description="Test description",
        website="https://test.com",
        industry="technology",
        sub_industries=["software", "ai"],
        business_model="SaaS",
        founded_year=2020,
        headquarters_country="RU",
        headquarters_city="Moscow",
        employees_count=50,
        employees_range="10-99",
        funding_total=None,
        funding_stage="Seed",
        last_funding_date=datetime.utcnow(),
        inn=None,
        ogrn=None,
        legal_name="Test Legal Name",
        tech_stack={"python": "3.12", "fastapi": "0.115"},
        integrations=["slack", "github"],
        api_available=True,
        ai_summary="AI summary",
        ai_tags=["tag1", "tag2"],
        embedding=[0.1, 0.2, 0.3],
        is_verified=True,
        view_count=100,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        deleted_at=None
    )