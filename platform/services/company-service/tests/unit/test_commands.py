import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime
from src.application.commands.create_company import CreateCompanyCommand
from src.application.commands.update_company import UpdateCompanyCommand
from src.application.commands.delete_company import DeleteCompanyCommand
from src.domain.company import Company
from src.infrastructure.repositories.company_repository import CompanyRepository
from src.infrastructure.kafka.producers import CompanyEventProducer
from src.domain.exceptions import CompanyNotFoundError


class TestCreateCompanyCommand:
    """Unit tests для CreateCompanyCommand."""

    @pytest.mark.asyncio
    async def test_create_company_success(self):
        """Проверка успешного создания компании."""
        # Моки зависимостей
        mock_repo = AsyncMock(spec=CompanyRepository)
        mock_producer = AsyncMock(spec=CompanyEventProducer)
        
        # Создаем команду
        command = CreateCompanyCommand(mock_repo, mock_producer)
        
        # Выполняем команду
        company_id = uuid4()
        result = await command.execute(
            name="Test Company",
            slug="test-company",
            industry="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Проверяем результат
        assert result == company_id
        
        # Проверяем вызовы моков
        mock_repo.create_from_domain.assert_called_once()
        mock_producer.produce_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_company_with_validation_error(self):
        """Проверка обработки ошибок валидации."""
        mock_repo = AsyncMock(spec=CompanyRepository)
        
        command = CreateCompanyCommand(mock_repo, mock_producer)
        
        # Попытка создать компанию с недопустимыми данными
        with pytest.raises(Exception) as exc_info:
            await command.execute(
                name="",  # Пустое имя - должно вызвать ошибку
                slug="test-company",
                industry="technology",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        
        assert "name" in str(exc_info.value)


class TestUpdateCompanyCommand:
    """Unit tests для UpdateCompanyCommand."""

    @pytest.mark.asyncio
    async def test_update_company_success(self):
        """Проверка успешного обновления компании."""
        # Моки зависимостей
        mock_repo = AsyncMock(spec=CompanyRepository)
        
        # Мокируем существующую компанию
        company_id = uuid4()
        existing_company = Company(
            id=company_id,
            name="Old Name",
            slug="old-slug",
            industry="old",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        mock_repo.get_by_id = AsyncMock(return_value=existing_company)
        
        # Создаем команду
        command = UpdateCompanyCommand(
            company_id=company_id,
            name="New Name",
            industry="new",
            mock_repo=mock_repo,
            event_producer=mock_producer
        )
        
        # Выполняем команду
        updated_company = await command.execute()
        
        # Проверяем результат
        assert updated_company.id == company_id
        assert updated_company.name == "New Name"
        assert updated_company.industry == "new"
        
        # Проверяем вызовы моков
        mock_repo.update_from_domain.assert_called_once()
        mock_producer.produce_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_company_not_found(self):
        """Проверка обработки отсутствующей компании."""
        mock_repo = AsyncMock(spec=CompanyRepository)
        
        # Мокируем отсутствие компании
        mock_repo.get_by_id = AsyncMock(return_value=None)
        
        command = UpdateCompanyCommand(
            company_id=uuid4(),
            name="New Name",
            mock_repo=mock_repo,
            event_producer=mock_producer
        )
        
        # Попытка обновить несуществующую компанию
        with pytest.raises(CompanyNotFoundError):
            await command.execute()


class TestDeleteCompanyCommand:
    """Unit tests для DeleteCompanyCommand."""

    @pytest.mark.asyncio
    async def test_delete_company_success(self):
        """Проверка успешного удаления компании."""
        # Моки зависимостей
        mock_repo = AsyncMock(spec=CompanyRepository)
        
        # Мокируем существующую компанию
        company_id = uuid4()
        mock_repo.soft_delete = AsyncMock(return_value=True)
        
        # Создаем команду
        command = DeleteCompanyCommand(company_id=company_id)
        
        # Выполняем команду
        success = await command.execute(mock_repo, None)
        
        # Проверяем результат
        assert success is True
        
        # Проверяем вызовы моков
        mock_repo.soft_delete.assert_called_once_with(company_id)

    @pytest.mark.asyncio
    async def test_delete_company_already_deleted(self):
        """Проверка обработки уже удаленной компании."""
        mock_repo = AsyncMock(spec=CompanyRepository)
        mock_repo.soft_delete = AsyncMock(return_value=False)
        
        command = DeleteCompanyCommand(company_id=uuid4())
        
        # Попытка удалить уже удаленную компанию
        with pytest.raises(CompanyNotFoundError):
            await command.execute(mock_repo, None)