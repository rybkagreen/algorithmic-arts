import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime
from src.application.queries.get_company import GetCompanyQuery
from src.application.queries.list_companies import ListCompaniesQuery
from src.application.queries.search_companies import SearchCompaniesQuery
from src.application.queries.get_similar_companies import GetSimilarCompaniesQuery
from src.domain.company import Company
from src.infrastructure.repositories.company_repository import CompanyRepository
from src.infrastructure.elasticsearch.company_indexer import CompanyIndexer
from src.domain.exceptions import CompanyNotFoundError


class TestGetCompanyQuery:
    """Unit tests для GetCompanyQuery."""

    @pytest.mark.asyncio
    async def test_get_company_success(self):
        """Проверка успешного получения компании."""
        # Моки зависимостей
        mock_repo = AsyncMock(spec=CompanyRepository)
        
        # Мокируем существующую компанию
        company_id = uuid4()
        company_data = Company(
            id=company_id,
            name="Test Company",
            slug="test-company",
            industry="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        mock_repo.get_by_id = AsyncMock(return_value=company_data)
        
        # Создаем query
        query = GetCompanyQuery(mock_repo)
        
        # Выполняем query
        result = await query.execute(company_id)
        
        # Проверяем результат
        assert result.id == company_id
        assert result.name == "Test Company"
        assert result.industry == "technology"

    @pytest.mark.asyncio
    async def test_get_company_not_found(self):
        """Проверка обработки отсутствующей компании."""
        mock_repo = AsyncMock(spec=CompanyRepository)
        mock_repo.get_by_id = AsyncMock(return_value=None)
        
        query = GetCompanyQuery(mock_repo)
        
        # Попытка получить несуществующую компанию
        with pytest.raises(CompanyNotFoundError):
            await query.execute(uuid4())


class TestListCompaniesQuery:
    """Unit tests для ListCompaniesQuery."""

    @pytest.mark.asyncio
    async def test_list_companies_success(self):
        """Проверка успешного получения списка компаний."""
        # Моки зависимостей
        mock_repo = AsyncMock(spec=CompanyRepository)
        
        # Мокируем список компаний
        company1 = Company(
            id=uuid4(),
            name="Company 1",
            slug="company1",
            industry="tech",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        company2 = Company(
            id=uuid4(),
            name="Company 2",
            slug="company2",
            industry="finance",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_repo.list_all = AsyncMock(return_value=[company1, company2])
        mock_repo.get_active_companies_count = AsyncMock(return_value=2)
        
        # Создаем query
        query = ListCompaniesQuery(mock_repo)
        
        # Выполняем query
        companies = await query.execute(skip=0, limit=10)
        
        # Проверяем результат
        assert len(companies) == 2
        assert companies[0].name == "Company 1"
        assert companies[1].name == "Company 2"
        
        # Проверка count
        count = await query.count_active()
        assert count == 2


class TestSearchCompaniesQuery:
    """Unit tests для SearchCompaniesQuery."""

    @pytest.mark.asyncio
    async def test_search_companies_by_name(self):
        """Проверка поиска компаний по имени."""
        # Моки зависимостей
        mock_repo = AsyncMock(spec=CompanyRepository)
        
        # Мокируем результаты поиска
        company1 = Company(
            id=uuid4(),
            name="Tech Company",
            slug="tech-company",
            industry="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_repo.search_by_name = AsyncMock(return_value=[company1])
        mock_repo.get_by_industry = AsyncMock(return_value=[])
        
        # Создаем query
        query = SearchCompaniesQuery(mock_repo)
        
        # Выполняем query по имени
        companies = await query.execute(name="Tech", skip=0, limit=10)
        
        # Проверяем результат
        assert len(companies) == 1
        assert companies[0].name == "Tech Company"

    @pytest.mark.asyncio
    async def test_search_companies_by_industry(self):
        """Проверка поиска компаний по отрасли."""
        # Моки зависимостей
        mock_repo = AsyncMock(spec=CompanyRepository)
        
        # Мокируем результаты поиска
        company1 = Company(
            id=uuid4(),
            name="Finance Company",
            slug="finance-company",
            industry="finance",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_repo.search_by_name = AsyncMock(return_value=[])
        mock_repo.get_by_industry = AsyncMock(return_value=[company1])
        
        # Создаем query
        query = SearchCompaniesQuery(mock_repo)
        
        # Выполняем query по отрасли
        companies = await query.execute(industry="finance", skip=0, limit=10)
        
        # Проверяем результат
        assert len(companies) == 1
        assert companies[0].industry == "finance"


class TestGetSimilarCompaniesQuery:
    """Unit tests для GetSimilarCompaniesQuery."""

    @pytest.mark.asyncio
    async def test_get_similar_companies_success(self):
        """Проверка успешного получения похожих компаний."""
        # Моки зависимостей
        mock_repo = AsyncMock(spec=CompanyRepository)
        mock_indexer = AsyncMock(spec=CompanyIndexer)
        
        # Мокируем существующую компанию
        company_id = uuid4()
        company = Company(
            id=company_id,
            name="Target Company",
            slug="target-company",
            industry="technology",
            embedding=[0.1, 0.2, 0.3],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        mock_repo.get_by_id = AsyncMock(return_value=company)
        
        # Мокируем результаты поиска по вектору
        mock_response = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {"_id": str(uuid4()), "_source": {"id": str(uuid4()), "name": "Similar Company 1", "industry": "technology"}},
                    {"_id": str(uuid4()), "_source": {"id": str(uuid4()), "name": "Similar Company 2", "industry": "technology"}}
                ]
            }
        }
        mock_indexer.get_similar_companies = AsyncMock(return_value=mock_response)
        
        # Создаем query
        query = GetSimilarCompaniesQuery(mock_repo, mock_indexer)
        
        # Выполняем query
        similar_companies = await query.execute(company_id=company_id, top_k=2)
        
        # Проверяем результат
        assert len(similar_companies) == 2
        assert similar_companies[0].name.startswith("Similar Company")