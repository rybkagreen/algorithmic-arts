from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Импортируем модули сервиса
from src.infrastructure.repositories.company_update_repository import CompanyUpdateRepository
from src.infrastructure.repositories.company_metric_repository import CompanyMetricRepository
from src.infrastructure.repositories.company_repository import CompanyRepository
from src.models import CompanyUpdate, CompanyMetric


class TestPartitionedTables:
    """Тесты для partitioned таблиц."""

    async def test_company_updates_partitioning_works(
        self, 
        db_session: AsyncSession,
        company_repo: CompanyRepository
    ):
        """Проверка, что company_updates правильно партиционирована по дате."""
        # Создаем компанию
        company_id = UUID("11111111-1111-1111-1111-111111111111")
        company_data = {
            "id": company_id,
            "name": "Test Company for Updates",
            "slug": "test-updates",
            "industry": "test",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db_company = company_repo.model_class(**company_data)
        db_session.add(db_company)
        await db_session.commit()
        await db_session.refresh(db_company)

        # Создаем репозиторий для updates
        update_repo = CompanyUpdateRepository(db_session)

        # Создаем обновления за разные месяцы
        today = datetime.utcnow()
        last_month = today - timedelta(days=30)
        next_month = today + timedelta(days=30)

        # Обновление за текущий месяц
        await update_repo.create_update(
            company_id=company_id,
            update_type="name_change",
            old_value={"name": "Old Name"},
            new_value={"name": "New Name 1"},
            changed_fields=["name"]
        )

        # Обновление за прошлый месяц
        update2 = await update_repo.create_update(
            company_id=company_id,
            update_type="industry_change",
            old_value={"industry": "old"},
            new_value={"industry": "new"},
            changed_fields=["industry"]
        )
        # Обновляем created_at для прошлого месяца
        await db_session.execute(
            update_repo.model_class.__table__.update()
            .where(update_repo.model_class.id == update2.id)
            .values(created_at=last_month)
        )
        await db_session.commit()

        # Обновление на следующий месяц (для проверки будущих партиций)
        update3 = await update_repo.create_update(
            company_id=company_id,
            update_type="website_change",
            old_value={"website": "old.com"},
            new_value={"website": "new.com"},
            changed_fields=["website"]
        )
        await db_session.execute(
            update_repo.model_class.__table__.update()
            .where(update_repo.model_class.id == update3.id)
            .values(created_at=next_month)
        )
        await db_session.commit()

        # Проверяем, что все обновления созданы
        total_updates = await db_session.execute(
            select(func.count()).select_from(CompanyUpdate)
        )
        assert total_updates.scalar() == 3

        # Проверяем, что можно получить обновления за конкретный период
        updates_current_month = await update_repo.get_updates_by_company(
            company_id=company_id,
            start_date=today - timedelta(days=15),
            end_date=today + timedelta(days=15)
        )
        assert len(updates_current_month) == 1  # Только update1

        updates_last_month = await update_repo.get_updates_by_company(
            company_id=company_id,
            start_date=last_month - timedelta(days=15),
            end_date=last_month + timedelta(days=15)
        )
        assert len(updates_last_month) == 1  # Только update2

        # Проверяем индексирование по company_id
        updates_by_company = await update_repo.get_updates_by_company(company_id=company_id)
        assert len(updates_by_company) == 3

    async def test_company_metrics_partitioning_works(
        self, 
        db_session: AsyncSession,
        company_repo: CompanyRepository
    ):
        """Проверка, что company_metrics правильно партиционирована по company_id."""
        # Создаем компанию
        company_id = UUID("22222222-2222-2222-2222-222222222222")
        company_data = {
            "id": company_id,
            "name": "Test Company for Metrics",
            "slug": "test-metrics",
            "industry": "test",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db_company = company_repo.model_class(**company_data)
        db_session.add(db_company)
        await db_session.commit()
        await db_session.refresh(db_company)

        # Создаем репозиторий для metrics
        metric_repo = CompanyMetricRepository(db_session)

        # Создаем метрики
        await metric_repo.create_metric(
            company_id=company_id,
            metric_type="revenue",
            value=100000.0,
            unit="RUB"
        )

        await metric_repo.create_metric(
            company_id=company_id,
            metric_type="users",
            value=5000.0,
            unit="count"
        )


        # Проверяем, что все метрики созданы
        total_metrics = await db_session.execute(
            select(func.count()).select_from(CompanyMetric)
        )
        assert total_metrics.scalar() == 3

        # Проверяем получение метрик по компании
        metrics_by_company = await metric_repo.get_metrics_by_company(company_id=company_id)
        assert len(metrics_by_company) == 3

        # Проверяем получение последней метрики по типу
        latest_revenue = await metric_repo.get_latest_metric(company_id=company_id, metric_type="revenue")
        assert latest_revenue is not None
        assert latest_revenue.value == 100000.0
        assert latest_revenue.metric_type == "revenue"

        # Проверяем фильтрацию по типу
        revenue_metrics = await metric_repo.get_metrics_by_company(
            company_id=company_id,
            metric_type="revenue"
        )
        assert len(revenue_metrics) == 1
        assert revenue_metrics[0].value == 100000.0

    async def test_soft_delete_handling_with_partitioned_tables(
        self, 
        db_session: AsyncSession,
        company_repo: CompanyRepository
    ):
        """Проверка, что soft delete работает корректно с partitioned таблицами."""
        # Создаем компанию
        company_id = UUID("33333333-3333-3333-3333-333333333333")
        company_data = {
            "id": company_id,
            "name": "Soft Delete Test Company",
            "slug": "soft-delete-test",
            "industry": "test",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db_company = company_repo.model_class(**company_data)
        db_session.add(db_company)
        await db_session.commit()
        await db_session.refresh(db_company)

        # Создаем репозитории
        update_repo = CompanyUpdateRepository(db_session)
        metric_repo = CompanyMetricRepository(db_session)

        # Создаем обновление и метрику


        # Проверяем, что данные существуют
        updates_count = await update_repo.count_updates_by_company(company_id)
        assert updates_count == 1

        metrics_count = await metric_repo.count_metrics_by_company(company_id)
        assert metrics_count == 1

        # Мягко удаляем компанию
        await db_session.execute(
            company_repo.model_class.__table__.update()
            .where(company_repo.model_class.id == company_id)
            .values(deleted_at=datetime.utcnow())
        )
        await db_session.commit()

        # Проверяем, что компания удалена (soft delete)
        company = await company_repo.get_by_id(company_id)
        assert company is None  # get_by_id возвращает только активные

        # Проверяем, что обновления и метрики все еще доступны (они не удаляются при soft delete компании)
        # Это ожидаемое поведение - исторические данные сохраняются
        updates_count_after_delete = await update_repo.count_updates_by_company(company_id)
        assert updates_count_after_delete == 1

        metrics_count_after_delete = await metric_repo.count_metrics_by_company(company_id)
        assert metrics_count_after_delete == 1