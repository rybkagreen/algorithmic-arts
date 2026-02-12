import pytest
from uuid import uuid4
from datetime import datetime
from src.domain.company import Company
from src.domain.events import CompanyCreated, CompanyUpdated, CompanyEnriched, CompanyMetricRecorded
from src.domain.value_objects import INN, OGRN, FundingAmount


class TestCompanyDomain:
    """Unit tests для domain модели Company."""

    def test_company_creation(self):
        """Проверка создания компании."""
        company_id = uuid4()
        company = Company.create(
            id=company_id,
            name="Test Company",
            slug="test-company",
            industry="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert company.id == company_id
        assert company.name == "Test Company"
        assert company.slug == "test-company"
        assert company.industry == "technology"
        assert len(company._domain_events) == 1
        assert isinstance(company._domain_events[0], CompanyCreated)
        assert company._domain_events[0].company_id == company_id
        assert company._domain_events[0].name == "Test Company"
        assert company._domain_events[0].industry == "technology"

    def test_company_update_with_changes(self):
        """Проверка обновления компании с изменениями."""
        company_id = uuid4()
        company = Company.create(
            id=company_id,
            name="Initial Name",
            slug="initial-slug",
            industry="initial",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Обновляем компанию
        company.update(
            name="Updated Name",
            industry="updated",
            website="https://updated.com"
        )

        assert company.name == "Updated Name"
        assert company.industry == "updated"
        assert company.website == "https://updated.com"
        assert len(company._domain_events) == 2  # Created + Updated
        assert isinstance(company._domain_events[1], CompanyUpdated)
        assert company._domain_events[1].company_id == company_id
        assert company._domain_events[1].changed_fields == ["name", "industry", "website"]

    def test_company_update_without_changes(self):
        """Проверка обновления компании без изменений."""
        company_id = uuid4()
        company = Company.create(
            id=company_id,
            name="Test Company",
            slug="test-company",
            industry="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Обновляем без изменений
        company.update(
            name="Test Company",
            industry="technology"
        )

        assert len(company._domain_events) == 1  # Только Created
        assert isinstance(company._domain_events[0], CompanyCreated)

    def test_company_enrich(self):
        """Проверка обогащения компании AI-данными."""
        company_id = uuid4()
        company = Company.create(
            id=company_id,
            name="Test Company",
            slug="test-company",
            industry="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Обогащаем компанию
        company.enrich(
            ai_summary="AI summary text",
            ai_tags=["tag1", "tag2"],
            embedding=[0.1, 0.2, 0.3]
        )

        assert company.ai_summary == "AI summary text"
        assert company.ai_tags == ["tag1", "tag2"]
        assert company.embedding == [0.1, 0.2, 0.3]
        assert len(company._domain_events) == 2  # Created + Enriched
        assert isinstance(company._domain_events[1], CompanyEnriched)
        assert company._domain_events[1].ai_summary == "AI summary text"
        assert company._domain_events[1].ai_tags == ["tag1", "tag2"]

    def test_company_record_metric(self):
        """Проверка записи метрики компании."""
        company_id = uuid4()
        company = Company.create(
            id=company_id,
            name="Test Company",
            slug="test-company",
            industry="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Записываем метрику
        company.record_metric(
            metric_type="revenue",
            value=100000.0,
            unit="RUB"
        )

        assert len(company._domain_events) == 2  # Created + MetricRecorded
        assert isinstance(company._domain_events[1], CompanyMetricRecorded)
        assert company._domain_events[1].metric_type == "revenue"
        assert company._domain_events[1].value == 100000.0
        assert company._domain_events[1].unit == "RUB"

    def test_company_to_dict(self):
        """Проверка преобразования компании в словарь."""
        company_id = uuid4()
        now = datetime.utcnow()
        company = Company.create(
            id=company_id,
            name="Test Company",
            slug="test-company",
            industry="technology",
            description="Test description",
            website="https://test.com",
            founded_year=2020,
            headquarters_country="RU",
            employees_count=50,
            funding_total=FundingAmount(amount=1000000.0, currency="USD"),
            inn=INN(value="1234567890"),
            ogrn=OGRN(value="1234567890123"),
            legal_name="Test Legal Name",
            tech_stack={"python": "3.12", "fastapi": "0.115"},
            integrations=["slack", "github"],
            api_available=True,
            is_verified=True,
            view_count=100,
            created_at=now,
            updated_at=now
        )

        company_dict = company.to_dict()

        assert company_dict["id"] == str(company_id)
        assert company_dict["name"] == "Test Company"
        assert company_dict["slug"] == "test-company"
        assert company_dict["industry"] == "technology"
        assert company_dict["description"] == "Test description"
        assert company_dict["website"] == "https://test.com"
        assert company_dict["founded_year"] == 2020
        assert company_dict["headquarters_country"] == "RU"
        assert company_dict["employees_count"] == 50
        assert company_dict["funding_total"] == {"amount": 1000000.0, "currency": "USD"}
        assert company_dict["inn"] == {"value": "1234567890"}
        assert company_dict["ogrn"] == {"value": "1234567890123"}
        assert company_dict["legal_name"] == "Test Legal Name"
        assert company_dict["tech_stack"] == {"python": "3.12", "fastapi": "0.115"}
        assert company_dict["integrations"] == ["slack", "github"]
        assert company_dict["api_available"] is True
        assert company_dict["is_verified"] is True
        assert company_dict["view_count"] == 100
        assert company_dict["created_at"] == now.isoformat()
        assert company_dict["updated_at"] == now.isoformat()
        assert company_dict["deleted_at"] is None

    def test_company_validation_errors(self):
        """Проверка валидации компании."""
        # Попытка создать компанию без обязательных полей
        with pytest.raises(Exception):
            Company.create(
                id=uuid4(),
                name="",  # Пустое имя - должно вызвать ошибку
                slug="test-slug",
                industry="technology",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )