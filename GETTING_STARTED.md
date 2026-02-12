# Руководство для разработчиков

**Версия:** 3.0  
**Дата:** Февраль 2026  
**Для:** Python 3.12+, Node.js 22+, Docker 24+

---

## 🎯 Что вам понадобится

### Обязательное ПО

```bash
# Проверьте версии (должны быть >= указанных)
docker --version        # Docker 24.0+
docker compose version  # Docker Compose 2.24+
python --version        # Python 3.12+
node --version          # Node.js 22+
git --version           # Git 2.40+
```

### Установка на разные ОС

**macOS (Homebrew):**
```bash
brew install docker
brew install python@3.12
brew install node@22
brew install postgresql@17
```

**Linux (Ubuntu/Debian):**
```bash
# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update && sudo apt install python3.12 python3.12-venv python3-pip

# Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

**Windows:**
```powershell
# Используйте winget или scoop
winget install Docker.DockerDesktop
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS

# Или через Chocolatey
choco install docker-desktop python nodejs-lts
```

---

## 🚀 Быстрый старт (5 минут)

### 1. Клонирование репозитория

```bash
git clone https://github.com/rybkagreen/algorithmic-arts.git
cd platform
```

### 2. Настройка окружения

```bash
# Копируем шаблоны конфигурации
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local

# Генерируем секретные ключи
python scripts/generate_secrets.py >> .env
```

### 3. Запуск инфраструктуры

```bash
# Поднимаем всю инфраструктуру
docker compose up -d

# Проверяем статус
docker compose ps
```

Ожидаемый вывод:
```
NAME                 STATUS    PORTS
postgres             Up        5432
redis                Up        6379
elasticsearch        Up        9200, 9300
kafka                Up        9092
api-gateway          Up        80
...
```

### 4. Применение миграций

```bash
# Ждём готовности PostgreSQL (30 сек)
docker compose exec -T postgres pg_isready -U algo_user

# Применяем миграции всех сервисов
docker compose exec api-gateway alembic upgrade head
docker compose exec company-service alembic upgrade head
docker compose exec auth-service alembic upgrade head
```

### 5. Загрузка тестовых данных

```bash
# Создаём первого админа
docker compose exec api-gateway python scripts/create_admin.py

# Загружаем 100 тестовых компаний
docker compose exec data-pipeline python scripts/seed_data.py --count=100
```

### 6. Проверка работы

```bash
# Health check всех сервисов
curl http://localhost/health

# Swagger UI
open http://localhost/docs

# Frontend
open http://localhost:3000
```

**Учетные данные по умолчанию:**
- Email: `admin@algorithmic-arts.ru`
- Password: `Admin123!ChangeMe`

⚠️ **ВАЖНО:** Смените пароль при первом входе!

---

## 📁 Структура проекта

```
platform/
│
├── services/                   # Backend микросервисы
│   ├── api-gateway/           # API Gateway (FastAPI)
│   ├── auth-service/          # Аутентификация
│   ├── user-service/          # Пользователи
│   ├── company-service/       # Компании
│   ├── partner-service/       # Партнёрства
│   ├── ai-core-service/       # AI + Agents
│   ├── data-pipeline/         # ETL + Парсинг
│   ├── crm-hub/              # CRM интеграции
│   ├── search-service/        # Поиск
│   ├── reporting/             # Отчёты
│   ├── billing/               # Биллинг
│   └── notification/          # Уведомления
│
├── frontend/                   # Next.js 15 приложение
│   ├── app/                   # App Router
│   ├── components/            # React компоненты
│   └── lib/                   # Утилиты
│
├── ai-agents/                  # AI агенты
│   ├── scout/                 # Partnership Scout
│   ├── analyzer/              # Compatibility Analyzer
│   ├── writer/                # Outreach Writer
│   └── orchestrator/          # Оркестратор
│
├── shared/                     # Общие библиотеки
│   ├── proto/                 # gRPC протоколы
│   ├── events/                # Event схемы
│   └── utils/                 # Утилиты
│
├── infra/                      # Инфраструктура
│   ├── terraform/             # IaC для Yandex Cloud
│   ├── kubernetes/            # K8s манифесты
│   └── helm-charts/           # Helm чарты
│
├── docs/                       # Документация
├── scripts/                    # Скрипты
├── tests/                      # Тесты
│
├── docker-compose.yml          # Локальная разработка
├── .env.example                # Шаблон переменных
└── README.md
```

---

## 🛠️ Разработка микросервиса

### Анатомия микросервиса

```
services/company-service/
│
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Конфигурация
│   │
│   ├── api/                    # HTTP endpoints
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── companies.py
│   │   │   └── health.py
│   │   └── dependencies.py
│   │
│   ├── grpc/                   # gRPC сервисы
│   │   ├── __init__.py
│   │   └── company_service.py
│   │
│   ├── domain/                 # Domain layer (DDD)
│   │   ├── __init__.py
│   │   ├── models.py           # Domain models
│   │   ├── events.py           # Domain events
│   │   └── services.py         # Domain services
│   │
│   ├── application/            # Application layer
│   │   ├── __init__.py
│   │   ├── commands.py         # CQRS commands
│   │   ├── queries.py          # CQRS queries
│   │   └── handlers.py         # Command/Query handlers
│   │
│   ├── infrastructure/         # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── database.py         # DB setup
│   │   ├── repositories.py     # Data access
│   │   ├── kafka_producer.py   # Event publishing
│   │   └── cache.py            # Redis caching
│   │
│   └── shared/                 # Shared kernel
│       ├── __init__.py
│       ├── schemas.py          # Pydantic models
│       └── exceptions.py       # Custom exceptions
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── versions/
│   └── alembic.ini
│
├── Dockerfile
├── pyproject.toml              # Poetry dependencies
├── .env.example
└── README.md
```

### Создание нового эндпоинта

```python
# src/api/v1/companies.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ...infrastructure.database import get_db
from ...application.queries import GetCompaniesQuery
from ...application.commands import CreateCompanyCommand
from ...shared.schemas import CompanyResponse, CompanyCreate
from ...api.dependencies import get_current_user

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("", response_model=list[CompanyResponse])
async def list_companies(
    industry: str | None = None,
    limit: int = 20,
    skip: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить список компаний с фильтрацией"""
    query = GetCompaniesQuery(db)
    companies = await query.execute(
        industry=industry,
        limit=limit,
        skip=skip
    )
    return companies

@router.post("", response_model=CompanyResponse, status_code=201)
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создать новую компанию"""
    command = CreateCompanyCommand(db)
    company = await command.execute(data, user_id=current_user.id)
    return company
```

### Работа с миграциями

```bash
# Создание новой миграции
cd services/company-service
poetry run alembic revision -m "add_company_rating_column"

# Редактирование миграции
nano alembic/versions/xxxx_add_company_rating_column.py

# Применение миграции
poetry run alembic upgrade head

# Откат последней миграции
poetry run alembic downgrade -1

# История миграций
poetry run alembic history

# Текущая версия
poetry run alembic current
```

### Event-Driven разработка

```python
# Публикация события
from shared.events import publish_event

async def create_company(data: CompanyCreate):
    # Создаём компанию в БД
    company = await db_repository.create(data)
    
    # Публикуем событие в Kafka
    await publish_event(
        topic="company.events",
        event_type="company.created",
        aggregate_id=str(company.id),
        payload={
            "id": str(company.id),
            "name": company.name,
            "industry": company.industry
        }
    )
    
    return company
```

```python
# Подписка на события (consumer)
from aiokafka import AIOKafkaConsumer

async def company_created_handler():
    consumer = AIOKafkaConsumer(
        'company.events',
        bootstrap_servers='kafka:9092',
        group_id='ai-enrichment-worker'
    )
    
    await consumer.start()
    try:
        async for msg in consumer:
            event = json.loads(msg.value)
            
            if event['event_type'] == 'company.created':
                # Запускаем AI обогащение
                await enrich_company_with_ai(event['aggregate_id'])
    finally:
        await consumer.stop()
```

---

## 🧪 Тестирование

### Unit тесты

```python
# tests/unit/test_companies.py
import pytest
from uuid import uuid4

from src.domain.models import Company
from src.application.commands import CreateCompanyCommand

@pytest.mark.asyncio
async def test_create_company(db_session):
    # Arrange
    command = CreateCompanyCommand(db_session)
    data = CompanyCreate(
        name="Test SaaS",
        industry="fintech",
        website="https://test.com"
    )
    
    # Act
    company = await command.execute(data, user_id=uuid4())
    
    # Assert
    assert company.name == "Test SaaS"
    assert company.industry == "fintech"
    assert company.id is not None
```

### Интеграционные тесты

```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_get_company(client: AsyncClient, auth_headers):
    # Create
    create_response = await client.post(
        "/api/v1/companies",
        json={
            "name": "Integration Test Co",
            "industry": "saas"
        },
        headers=auth_headers
    )
    assert create_response.status_code == 201
    company_id = create_response.json()["id"]
    
    # Get
    get_response = await client.get(
        f"/api/v1/companies/{company_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Integration Test Co"
```

### Запуск тестов

```bash
# Все тесты
docker compose exec company-service poetry run pytest

# Только unit
docker compose exec company-service poetry run pytest tests/unit/ -v

# Только integration
docker compose exec company-service poetry run pytest tests/integration/ -v

# С покрытием
docker compose exec company-service poetry run pytest --cov=src --cov-report=html

# Открыть отчёт
open htmlcov/index.html
```

---

## 🐛 Отладка

### VS Code Launch Configuration

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Company Service",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8003"
      ],
      "cwd": "${workspaceFolder}/services/company-service",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/services/company-service"
      },
      "justMyCode": true
    }
  ]
}
```

### Логирование

```python
# Structured logging с structlog
import structlog

logger = structlog.get_logger(__name__)

async def create_company(data: CompanyCreate):
    logger.info(
        "creating_company",
        company_name=data.name,
        industry=data.industry
    )
    
    try:
        company = await repository.create(data)
        logger.info(
            "company_created",
            company_id=str(company.id)
        )
        return company
    except Exception as e:
        logger.error(
            "company_creation_failed",
            error=str(e),
            exc_info=True
        )
        raise
```

### Просмотр логов

```bash
# Логи всех сервисов
docker compose logs -f

# Логи одного сервиса
docker compose logs -f company-service

# Последние 100 строк
docker compose logs --tail=100 company-service

# Поиск по логам
docker compose logs company-service | grep ERROR

# Логи в JSON для анализа
docker compose logs --no-color company-service | jq '.level == "error"'
```

---

## 🔧 Полезные команды

### Docker

```bash
# Пересборка после изменений
docker compose up -d --build

# Остановка всех сервисов
docker compose down

# Остановка + удаление данных
docker compose down -v

# Рестарт одного сервиса
docker compose restart company-service

# Просмотр ресурсов
docker stats

# Очистка неиспользуемых ресурсов
docker system prune -a
```

### База данных

```bash
# Подключение к PostgreSQL
docker compose exec postgres psql -U algo_user -d algorithmic_arts

# Резервная копия
docker compose exec postgres pg_dump -U algo_user algorithmic_arts > backup.sql

# Восстановление
cat backup.sql | docker compose exec -T postgres psql -U algo_user algorithmic_arts

# Просмотр активных подключений
docker compose exec postgres psql -U algo_user -d algorithmic_arts -c \
  "SELECT pid, usename, application_name, client_addr FROM pg_stat_activity;"
```

### Git

```bash
# Создание feature ветки
git checkout -b feature/add-company-tags

# Коммит (Conventional Commits)
git commit -m "feat(company): добавить систему тегов"

# Типы коммитов:
# feat:     новая функция
# fix:      исправление бага
# docs:     документация
# style:    форматирование
# refactor: рефакторинг
# test:     тесты
# chore:    техническая задача

# Push ветки
git push origin feature/add-company-tags

# Обновление main
git checkout main
git pull origin main

# Rebase на актуальную main
git checkout feature/add-company-tags
git rebase main
```

---

## 📚 Дополнительные ресурсы

- **Архитектура:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **API документация:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Развёртывание:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Тестирование:** [TESTING.md](TESTING.md)
- **Промпты для AI:** [PROMPTS_FOR_QWEN.md](PROMPTS_FOR_QWEN.md)

---

## ❓ Частые вопросы

**Q: Сервис не запускается, ошибка "port already in use"**

A: Проверьте занятые порты:
```bash
lsof -i :8003  # Замените на нужный порт
# Убейте процесс или измените порт в docker-compose.yml
```

**Q: Миграции не применяются**

A: Проверьте готовность БД и последовательность:
```bash
docker compose exec postgres pg_isready
docker compose exec company-service alembic current
docker compose exec company-service alembic upgrade head
```

**Q: Как добавить новую зависимость?**

A:
```bash
cd services/company-service
poetry add langchain
poetry lock
docker compose up -d --build company-service
```

---

**Последнее обновление:** Февраль 2026  
**Версия:** 3.0
