# Промпты для генерации кода платформы ALGORITHMIC ARTS

**Версия:** 3.0  
**Дата:** Февраль 2026  
**Для:** Qwen Code, Claude, GPT-4, или любая AI с coding capabilities

---

## 📋 Оглавление промптов

1. [Промпт №1: Инфраструктура и Docker Compose](#промпт-1-инфраструктура)
2. [Промпт №2: Базы данных и миграции](#промпт-2-базы-данных)
3. [Промпт №3: Auth + User Service](#промпт-3-auth-user-service)
4. [Промпт №4: Company + Partner Service](#промпт-4-company-partner-service)
5. [Промпт №5: AI Core + Multi-Agent System](#промпт-5-ai-core)
6. [Промпт №6: Data Pipeline + Parsers](#промпт-6-data-pipeline)
7. [Промпт №7: CRM Hub + Integrations](#промпт-7-crm-hub)
8. [Промпт №8: Frontend Next.js 15](#промпт-8-frontend)
9. [Промпт №9: DevOps + Kubernetes](#промпт-9-devops)

---

## Промпт №1: Инфраструктура

### Задача
Создать базовую инфраструктуру проекта: структуру директорий, Docker Compose, основные конфигурационные файлы.

### Промпт

```markdown
Создай полную инфраструктуру для микросервисной платформы ALGORITHMIC ARTS.

ТРЕБОВАНИЯ:

1. СТРУКТУРА ПРОЕКТА:
```
platform/
├── services/
│   ├── api-gateway/
│   ├── auth-service/
│   ├── user-service/
│   ├── company-service/
│   ├── partner-service/
│   ├── ai-core-service/
│   ├── data-pipeline/
│   ├── crm-hub/
│   ├── search-service/
│   ├── reporting/
│   ├── billing/
│   └── notification/
├── frontend/
├── ai-agents/
├── shared/
├── infra/
├── scripts/
└── tests/
```

2. DOCKER COMPOSE (docker-compose.yml):
- PostgreSQL 17 (с pgvector, pg_cron, Citus)
- Redis Stack 7.4
- Elasticsearch 8.14
- Apache Kafka 3.7 + Zookeeper
- MinIO (S3-compatible)
- Prometheus + Grafana
- Loki (логирование)
- Jaeger (трейсинг)

3. ФАЙЛ .env.example со всеми переменными:
- Подключения к БД
- API ключи (YandexGPT, GigaChat, OpenRouter)
- CRM интеграции (amoCRM, Битрикс24)
- JWT секреты
- Email, Telegram
- Платёжные системы

4. БАЗОВЫЕ КОНФИГУРАЦИИ:
- pyproject.toml для каждого сервиса (Poetry)
- Dockerfile для каждого сервиса (multi-stage build)
- .gitignore
- .dockerignore
- Makefile с полезными командами

5. СКРИПТЫ:
- scripts/generate_secrets.py (генерация JWT, паролей)
- scripts/check_dependencies.sh (проверка версий)
- scripts/init_project.sh (первичная инициализация)

ТЕХНОЛОГИИ:
- Python 3.12
- FastAPI 0.115+
- PostgreSQL 17
- Redis Stack 7.4
- Node.js 22
- Next.js 15

Создай полную структуру со всеми файлами. Каждый Dockerfile должен быть production-ready с multi-stage builds.
```

---

## Промпт №2: Базы данных

### Задача
Создать схемы баз данных, миграции Alembic для всех микросервисов.

### Промпт

```markdown
Создай полные схемы PostgreSQL баз данных для платформы ALGORITHMIC ARTS.

ТРЕБУЕМЫЕ ТАБЛИЦЫ:

1. AUTH DATABASE:
- users (id UUID, email, password_hash bcrypt, full_name, company_name, role, is_active, 2FA)
- sessions (id, user_id, token, expires_at)
- oauth_connections (id, user_id, provider, external_id)
- permissions (id, name, description)
- roles (id, name, permissions[])
- user_roles (user_id, role_id)

2. COMPANY DATABASE:
- companies (id UUID, name, slug, description, website, logo_url, industry, sub_industries[], business_model, founded_year, headquarters_country, headquarters_city, employees_count, employees_range, funding_total, funding_stage, last_funding_date, inn, ogrn, kpp, legal_name, tech_stack JSONB, integrations[], api_available, ai_summary, ai_tags[], embedding VECTOR(1536), is_verified, view_count, created_at, updated_at, deleted_at)
- company_updates (id, company_id, update_type, title, content, source_url, published_at)
- company_metrics (id, company_id, metric_name, metric_value, measured_at)

3. PARTNERSHIP DATABASE:
- partnerships (id, company_a_id, company_b_id, compatibility_score NUMERIC(3,2), match_reasons[], synergy_areas[], analysis_method, analyzed_by_agent, ai_explanation, status, contacted_at, partnership_started_at, deal_value, revenue_generated)
- outreach_messages (id, partnership_id, message_text, sent_at, response_received, response_text)

4. CRM DATABASE:
- crm_connections (id, user_id, crm_type ENUM('amocrm', 'bitrix24', 'salesforce'), access_token, refresh_token, expires_at, account_subdomain)
- crm_sync_logs (id, connection_id, direction ENUM('to_crm', 'from_crm'), entity_type, entity_id, status, error_message, synced_at)

5. BILLING DATABASE:
- subscriptions (id, user_id, plan ENUM('starter', 'growth', 'scale', 'enterprise'), status ENUM('active', 'cancelled', 'past_due'), current_period_start, current_period_end, cancel_at_period_end)
- payments (id, subscription_id, amount, currency DEFAULT 'RUB', status, payment_method, external_payment_id, paid_at)

ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ:
- Все таблицы должны иметь created_at, updated_at (с триггерами)
- Индексы на все foreign keys
- VECTOR индексы для pgvector (IVFFlat)
- GIN индексы для JSONB и массивы
- Партиционирование для больших таблиц (company_updates, company_metrics по дате)
- Soft delete (deleted_at IS NULL)

Создай:
1. SQL схемы для создания таблиц
2. Миграции Alembic для каждого сервиса (services/*/alembic/versions/)
3. SQLAlchemy модели (services/*/src/models.py)
4. Seed данные для тестирования (100 компаний, 50 пользователей)
```

---

## Промпт №3: Auth + User Service

### Задача
Реализовать полноценную аутентификацию и управление пользователями.

### Промпт

```markdown
Создай полные микросервисы Auth и User для платформы ALGORITHMIC ARTS.

AUTH-SERVICE (порт 8001):

1. ЭНДПОИНТЫ:
POST   /auth/register           # Регистрация с email verification
POST   /auth/login              # Вход (email/password)
POST   /auth/logout             # Выход
POST   /auth/refresh            # Refresh токена
POST   /auth/oauth/{provider}   # OAuth2 (Яндекс, Google, VK)
POST   /auth/2fa/setup          # Настройка 2FA (TOTP)
POST   /auth/2fa/verify         # Верификация 2FA
POST   /auth/password/reset     # Запрос сброса пароля
POST   /auth/password/confirm   # Подтверждение нового пароля
GET    /auth/me                 # Текущий пользователь

2. JWT IMPLEMENTATION:
- Access token (15 мин)
- Refresh token (30 дней)
- RS256 подпись (private/public keys)
- Ротация ключей
- Blacklist токенов в Redis

3. БЕЗОПАСНОСТЬ:
- Bcrypt для паролей (cost 12)
- Rate limiting (5 попыток / 5 минут)
- Email verification обязателен
- 2FA опционален (TOTP через pyotp)
- CSRF защита
- Защита от timing attacks

USER-SERVICE (порт 8002):

1. ЭНДПОИНТЫ:
GET    /users/me                    # Профиль текущего пользователя
PUT    /users/me                    # Обновление профиля
GET    /users/{user_id}             # Получить пользователя
PUT    /users/{user_id}             # Обновить пользователя (админ)
DELETE /users/{user_id}             # Удалить (soft delete)
POST   /users/{user_id}/preferences # Настройки уведомлений
GET    /users/{user_id}/activity    # История активности
POST   /users/team                  # Пригласить в команду
DELETE /users/team/{member_id}      # Удалить из команды

2. RBAC IMPLEMENTATION:
- Роли: free_user, paid_user, company_admin, platform_admin
- Permissions: company:read, company:write, etc.
- Проверка прав в dependencies
- ABAC для владения ресурсами

3. ИНТЕГРАЦИИ:
- Kafka events (user.created, user.updated)
- Redis кэширование профилей (TTL 1 час)
- Elasticsearch для поиска пользователей

ОБЩИЕ ТРЕБОВАНИЯ:
- FastAPI с async/await
- Pydantic для валидации
- SQLAlchemy 2.0 (async)
- Alembic миграции
- 90%+ test coverage
- OpenAPI документация
- Structured logging (structlog)
- Health checks (/health)
- Metrics (Prometheus)

Создай полную реализацию обоих сервисов со всеми файлами.
```

---

## Промпт №4: Company + Partner Service

### Задача
Реализовать CRUD компаний и логику подбора партнёров.

### Промпт

```markdown
Создай Company Service и Partner Service для ALGORITHMIC ARTS.

COMPANY-SERVICE (порт 8003):

1. ЭНДПОИНТЫ:
GET    /companies                   # Список с фильтрацией
GET    /companies/{company_id}      # Детальная информация
POST   /companies                   # Создать компанию (админ)
PUT    /companies/{company_id}      # Обновить компанию
DELETE /companies/{company_id}      # Удалить (soft delete)
GET    /companies/search            # Полнотекстовый поиск
GET    /companies/{id}/similar      # Похожие компании (vector search)
POST   /companies/{id}/enrich       # Запустить AI обогащение
GET    /companies/{id}/history      # История изменений
POST   /companies/batch             # Пакетное создание

2. ФИЛЬТРАЦИЯ:
- По индустрии, региону, размеру компании
- По технологиям (tech_stack)
- По наличию финансирования
- По дате основания
- Комбинированные фильтры

3. VECTOR SEARCH:
- Генерация эмбеддингов через Sentence Transformers
- Хранение в pgvector
- Similarity search (cosine distance)
- Hybrid search (full-text + vector)

4. EVENT SOURCING:
- Все изменения как события
- Kafka topics: company.created, company.updated
- Event store в PostgreSQL
- Snapshots каждые 100 событий

PARTNER-SERVICE (порт 8004):

1. ЭНДПОИНТЫ:
GET    /partnerships                      # Список партнёрств
GET    /partnerships/{partnership_id}     # Детали
POST   /partnerships/analyze              # Анализ совместимости
POST   /partnerships/{id}/contact         # Отправить outreach
PUT    /partnerships/{id}/status          # Обновить статус
GET    /partnerships/recommendations      # Рекомендации для компании
GET    /partnerships/stats                # Статистика

2. COMPATIBILITY ALGORITHM:
```python
def calculate_compatibility(company_a, company_b):
    scores = {
        'tech_compatibility': check_tech_stack_overlap(),
        'market_overlap': check_target_market(),
        'size_match': check_company_size_compatibility(),
        'geo_proximity': check_geographical_match(),
        'no_competition': check_not_direct_competitors(),
        'complementarity': check_feature_complementarity()
    }
    
    # Взвешенная сумма
    weights = [0.25, 0.20, 0.15, 0.10, 0.15, 0.15]
    final_score = sum(s * w for s, w in zip(scores.values(), weights))
    
    return final_score
```

3. REAL-TIME MATCHING:
- Kafka consumer для company.created
- Автоматический поиск партнёров
- AI анализ через ai-core-service (gRPC)
- Уведомления при score > 0.7

4. REPORTING:
- Генерация PDF отчётов (WeasyPrint)
- Excel экспорты (openpyxl)
- Графики (Plotly)

ОБЩИЕ ТРЕБОВАНИЯ:
- CQRS pattern (команды vs запросы)
- Repository pattern
- Domain-Driven Design
- Event-Driven Architecture
- Кэширование в Redis (read-through)
- Pagination (cursor-based)
- Rate limiting
- Monitoring

Создай полную реализацию со всеми слоями архитектуры (domain, application, infrastructure).
```

---

## Промпт №5: AI Core

### Задача
Создать AI движок с мультиагентной системой.

### Промпт

```markdown
Создай AI Core Service с мультиагентной архитектурой для ALGORITHMIC ARTS.

AI-CORE-SERVICE (порт 8005):

1. ЭНДПОИНТЫ:
POST   /ai/enrich/company           # Обогатить данные компании
POST   /ai/find/similar             # Найти похожие компании
POST   /ai/analyze/compatibility    # Анализ совместимости
POST   /ai/generate/summary         # Генерация краткого описания
POST   /ai/generate/pitch           # Генерация pitch-письма
POST   /ai/analyze/news             # Анализ новости компании
POST   /ai/rank/partners            # Ранжирование партнёров
POST   /ai/embedding/generate       # Генерация эмбеддинга
POST   /ai/chat                     # Чат с AI ассистентом
GET    /ai/models/available         # Список доступных моделей

2. LLM ROUTER (с фолбэком):
```python
class LLMRouter:
    def __init__(self):
        self.providers = [
            YandexGPTProvider(priority=1),
            GigaChatProvider(priority=2),
            OpenRouterProvider(priority=3, models=['claude-sonnet-4', 'gpt-4o'])
        ]
    
    async def generate(self, prompt, max_retries=3):
        for provider in sorted(self.providers, key=lambda p: p.priority):
            try:
                response = await provider.generate(prompt)
                # Log успешный вызов
                await log_llm_usage(provider.name, success=True)
                return response
            except Exception as e:
                # Log ошибку и пробуем следующий
                await log_llm_usage(provider.name, success=False, error=str(e))
                continue
        
        raise AllProvidersFailedError()
```

3. MULTI-AGENT SYSTEM (LangGraph):

**Agent 1: Partnership Scout**
- Мониторит VC.ru, Habr, LinkedIn
- Находит новые компании и изменения
- Триггер: каждые 15 минут

**Agent 2: Compatibility Analyzer**
- Анализирует совместимость продуктов
- Векторный поиск + LLM оценка
- Триггер: новая компания или запрос пользователя

**Agent 3: Outreach Writer**
- Генерирует персонализированные письма
- Стили: формальный, дружеский, техничный
- Триггер: пользователь нажимает "Contact"

**Agent 4: Data Enricher**
- Обогащает профили компаний
- Парсит сайты, соцсети, новости
- Триггер: новая компания или по расписанию

**Agent 5: Analytics Predictor**
- Предсказывает вероятность сделки
- Gradient Boosting модель
- Триггер: обновление данных партнёрства

4. ORCHESTRATOR (LangGraph):
```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("scout", scout_agent)
workflow.add_node("analyzer", analyzer_agent)
workflow.add_node("writer", writer_agent)
workflow.add_node("enricher", enricher_agent)

# Edges
workflow.add_edge("scout", "enricher")
workflow.add_edge("enricher", "analyzer")
workflow.add_conditional_edges(
    "analyzer",
    should_generate_outreach,
    {"yes": "writer", "no": END}
)

graph = workflow.compile()
```

5. EMBEDDINGS:
- Sentence Transformers (multilingual)
- Модель: sentence-transformers/paraphrase-multilingual-mpnet-base-v2
- Размерность: 768
- Batch processing
- Кэширование в Redis

6. RAG (Retrieval-Augmented Generation):
- Vector store: pgvector
- Retriever: Hybrid (dense + BM25)
- Re-ranker: Cross-encoder
- Context window: 8000 tokens

ТРЕБОВАНИЯ:
- LangChain для оркестрации
- AsyncIO для параллелизма
- Celery для фоновых задач
- Prometheus метрики (время генерации, стоимость)
- Graceful degradation при недоступности LLM
- A/B тестирование промптов

Создай полную реализацию всех агентов и оркестратора.
```

---

## Промпт №6: Data Pipeline

### Задача
Создать ETL пайплайн для сбора данных о компаниях.

### Промпт

```markdown
Создай Data Pipeline Service для автоматического сбора данных о российских SaaS компаниях.

DATA-PIPELINE-SERVICE (порт 8006):

1. ИСТОЧНИКИ ДАННЫХ:

**A. VC.ru**
- RSS фид: https://vc.ru/rss
- Парсинг статей о стартапах
- Извлечение: название, описание, раунды
- Частота: каждый час

**B. Rusbase**
- API + Web scraping
- Новости о инвестициях
- База стартапов
- Частота: каждые 2 часа

**C. Habr Карьера**
- API вакансий
- Определение стека технологий
- Размер команды
- Частота: ежедневно

**D. ЕГРЮЛ (Контур.Фокус)**
- API для проверки ИНН/ОГРН
- Юридическая информация
- Финансовые показатели
- Частота: при создании компании

**E. Crunchbase (международные)**
- API для глобальных компаний
- Данные о финансировании
- Частота: еженедельно

2. SCRAPERS (Scrapy):

```python
# scraper_vc_ru.py
class VCRuSpider(scrapy.Spider):
    name = 'vc_ru'
    
    def start_requests(self):
        yield scrapy.Request('https://vc.ru/rss', self.parse_rss)
    
    def parse_rss(self, response):
        # Парсинг RSS
        for item in response.xpath('//item'):
            article_url = item.xpath('link/text()').get()
            yield scrapy.Request(article_url, self.parse_article)
    
    def parse_article(self, response):
        # Извлечение данных о компании
        company_data = {
            'name': extract_company_name(response),
            'description': extract_description(response),
            'funding_amount': extract_funding(response),
            'source_url': response.url
        }
        
        # Отправка в Kafka
        yield company_data
```

3. ETL PIPELINE:

**Extract:**
- Scrapy для веб-скрейпинга
- API клиенты для официальных источников
- Расписание через Celery Beat

**Transform:**
- Очистка HTML
- NER для извлечения сущностей (компании, суммы)
- Дедупликация (fuzzy matching названий)
- Валидация (Pydantic схемы)

**Load:**
- Kafka producer → company.raw_data topic
- Batch insert в PostgreSQL
- Обновление Elasticsearch индекса

4. НОРМАЛИЗАЦИЯ:

```python
async def normalize_company_data(raw_data: dict) -> CompanyData:
    # 1. Нормализация названия
    name = clean_company_name(raw_data['name'])
    
    # 2. Парсинг суммы финансирования
    funding = parse_funding_amount(raw_data.get('funding_text'))
    
    # 3. Категоризация индустрии (ML classifier)
    industry = classify_industry(raw_data['description'])
    
    # 4. Извлечение технологий
    tech_stack = extract_technologies(raw_data['description'])
    
    # 5. Геолокация
    location = geocode_location(raw_data.get('location'))
    
    return CompanyData(
        name=name,
        funding_total=funding,
        industry=industry,
        tech_stack=tech_stack,
        headquarters_city=location
    )
```

5. ДЕДУПЛИКАЦИЯ:

```python
from fuzzywuzzy import fuzz

async def find_duplicates(new_company: CompanyData):
    # Поиск похожих названий
    candidates = await db.query(
        "SELECT id, name FROM companies WHERE name ILIKE %s",
        f"%{new_company.name[:5]}%"
    )
    
    for candidate in candidates:
        # Similarity score
        score = fuzz.ratio(new_company.name.lower(), candidate.name.lower())
        
        if score > 85:
            # Потенциальный дубликат
            return candidate.id
    
    return None
```

6. РАСПИСАНИЕ (Celery Beat):

```python
from celery import Celery
from celery.schedules import crontab

app = Celery('data_pipeline')

app.conf.beat_schedule = {
    'scrape-vc-ru': {
        'task': 'tasks.scrape_vc_ru',
        'schedule': crontab(minute=0, hour='*/1'),  # Каждый час
    },
    'scrape-rusbase': {
        'task': 'tasks.scrape_rusbase',
        'schedule': crontab(minute=0, hour='*/2'),  # Каждые 2 часа
    },
    'update-egrul': {
        'task': 'tasks.update_egrul_data',
        'schedule': crontab(hour=3, minute=0),  # 3:00 AM daily
    },
}
```

7. МОНИТОРИНГ:
- Количество обработанных источников
- Новые компании за день
- Ошибки парсинга
- Время выполнения задач
- Алерты в Telegram при критических ошибках

ТРЕБОВАНИЯ:
- Scrapy + Selenium (для динамических сайтов)
- Celery + Redis для задач
- Kafka для event streaming
- PostgreSQL для хранения
- Anti-bot меры (User-Agent rotation, delays)
- Retry логика (3 попытки с exponential backoff)

Создай полные scrapers и ETL pipeline.
```

---

## Промпт №7: CRM Hub

### Задача
Создать унифицированный хаб для интеграции с российскими и международными CRM.

### Промпт

```markdown
Создай CRM Hub Service с унифицированной интеграцией для всех популярных CRM систем.

CRM-HUB-SERVICE (порт 8007):

1. ПОДДЕРЖИВАЕМЫЕ CRM:

**Российские:**
- amoCRM (основной для РФ)
- Битрикс24
- Мегаплан

**Международные:**
- Salesforce
- HubSpot
- Pipedrive

2. ЭНДПОИНТЫ:

POST   /crm/connect/{crm_type}        # OAuth подключение
GET    /crm/connections               # Список подключений
DELETE /crm/connections/{id}          # Отключить CRM
POST   /crm/sync/manual              # Ручная синхронизация
GET    /crm/sync/status              # Статус последней синхронизации
POST   /crm/leads/create             # Создать лид
PUT    /crm/leads/{id}/update        # Обновить лид
GET    /crm/leads/{id}               # Получить лид
POST   /crm/contacts/create          # Создать контакт
GET    /crm/webhooks/{crm_type}      # Webhook endpoint

3. АБСТРАКТНЫЙ ИНТЕРФЕЙС:

```python
from abc import ABC, abstractmethod

class BaseCRMAdapter(ABC):
    @abstractmethod
    async def authorize(self, code: str) -> CRMConnection:
        """OAuth authorization"""
        pass
    
    @abstractmethod
    async def create_lead(self, lead_data: LeadData) -> str:
        """Create lead, return external_id"""
        pass
    
    @abstractmethod
    async def update_lead(self, external_id: str, updates: dict) -> bool:
        """Update lead"""
        pass
    
    @abstractmethod
    async def get_lead(self, external_id: str) -> LeadData:
        """Get lead details"""
        pass
    
    @abstractmethod
    async def sync_from_crm(self) -> list[LeadData]:
        """Pull leads from CRM"""
        pass
```

4. AMOCRM ADAPTER:

```python
class AmoCRMAdapter(BaseCRMAdapter):
    def __init__(self, connection: CRMConnection):
        self.subdomain = connection.account_subdomain
        self.access_token = connection.access_token
        self.base_url = f"https://{self.subdomain}.amocrm.ru/api/v4"
    
    async def create_lead(self, lead_data: LeadData) -> str:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        payload = {
            "name": lead_data.title,
            "price": lead_data.deal_value,
            "custom_fields_values": [
                {
                    "field_code": "COMPANY_NAME",
                    "values": [{"value": lead_data.company_name}]
                },
                {
                    "field_code": "COMPATIBILITY_SCORE",
                    "values": [{"value": str(lead_data.compatibility_score)}]
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/leads",
                json=[payload],
                headers=headers
            )
            
            response.raise_for_status()
            data = response.json()
            return str(data["_embedded"]["leads"][0]["id"])
    
    async def sync_from_crm(self) -> list[LeadData]:
        # Получить все лиды из amoCRM
        # Конвертировать в внутренний формат
        # Обновить нашу БД
        pass
```

5. BITRIX24 ADAPTER:

```python
class Bitrix24Adapter(BaseCRMAdapter):
    def __init__(self, connection: CRMConnection):
        self.webhook_url = f"https://{connection.account_subdomain}.bitrix24.ru/rest/{connection.user_id}/{connection.access_token}"
    
    async def create_lead(self, lead_data: LeadData) -> str:
        payload = {
            "fields": {
                "TITLE": lead_data.title,
                "COMPANY_TITLE": lead_data.company_name,
                "OPPORTUNITY": lead_data.deal_value,
                "UF_CRM_COMPATIBILITY": lead_data.compatibility_score
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.webhook_url}/crm.lead.add",
                json=payload
            )
            
            data = response.json()
            return str(data["result"])
```

6. СИНХРОНИЗАЦИЯ:

**Направления:**
- TO_CRM: Партнёрства из платформы → Лиды в CRM
- FROM_CRM: Обновления лидов в CRM → Обновления партнёрств

**Стратегии конфликтов:**
```python
class ConflictResolutionStrategy(Enum):
    CRM_WINS = "crm_wins"           # CRM приоритетнее
    PLATFORM_WINS = "platform_wins" # Платформа приоритетнее
    LAST_MODIFIED_WINS = "last_modified"  # Последнее изменение
    MANUAL_REVIEW = "manual"        # Требует ручного разрешения
```

7. WEBHOOKS:

```python
@router.post("/crm/webhooks/amocrm")
async def amocrm_webhook(request: Request):
    payload = await request.json()
    
    event_type = payload.get("leads[status][0][status_id]")
    lead_id = payload.get("leads[status][0][id]")
    
    if event_type == "142":  # Статус "Успешно реализовано"
        # Обновить партнёрство в нашей БД
        await update_partnership_status(
            crm_type="amocrm",
            external_id=lead_id,
            status="active"
        )
    
    return {"status": "ok"}
```

8. МАППИНГ ПОЛЕЙ:

```python
FIELD_MAPPINGS = {
    "amocrm": {
        "company_name": "COMPANY_NAME",
        "contact_person": "NAME",
        "compatibility_score": "COMPATIBILITY_SCORE",
        "deal_value": "price",
    },
    "bitrix24": {
        "company_name": "COMPANY_TITLE",
        "contact_person": "NAME",
        "compatibility_score": "UF_CRM_COMPATIBILITY",
        "deal_value": "OPPORTUNITY",
    },
}
```

ТРЕБОВАНИЯ:
- OAuth 2.0 для всех CRM
- Refresh token автоматически
- Webhook обработка
- Batch синхронизация (каждые 15 минут)
- Conflict resolution
- Audit log всех изменений
- Retry логика

Создай полную реализацию CRM Hub со всеми адаптерами.
```

---

## Промпт №8: Frontend

### Задача
Создать современный Next.js 15 фронтенд.

### Промпт

```markdown
Создай полноценный Next.js 15 frontend для платформы ALGORITHMIC ARTS.

ТЕХНОЛОГИИ:
- Next.js 15 (App Router)
- React 19
- TypeScript 5.4
- Tailwind CSS 3.4
- shadcn/ui
- TanStack Query
- Zustand (state management)

СТРУКТУРА:
```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── companies/
│   │   │   ├── page.tsx              # Список компаний
│   │   │   ├── [id]/page.tsx         # Детали компании
│   │   │   └── new/page.tsx          # Создание компании
│   │   ├── partnerships/
│   │   │   ├── page.tsx              # Список партнёрств
│   │   │   ├── recommendations/page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── analytics/page.tsx
│   │   ├── settings/page.tsx
│   │   └── layout.tsx
│   ├── api/
│   │   └── auth/[...nextauth]/route.ts
│   ├── layout.tsx
│   └── page.tsx                      # Landing page
├── components/
│   ├── ui/                           # shadcn/ui components
│   ├── companies/
│   │   ├── CompanyCard.tsx
│   │   ├── CompanyFilters.tsx
│   │   └── CompanySearch.tsx
│   ├── partnerships/
│   │   ├── PartnershipCard.tsx
│   │   ├── CompatibilityScore.tsx
│   │   └── OutreachDialog.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/
│   ├── api/
│   │   ├── client.ts             # Axios instance
│   │   ├── companies.ts
│   │   ├── partnerships.ts
│   │   └── auth.ts
│   ├── hooks/
│   │   ├── useCompanies.ts
│   │   ├── usePartnerships.ts
│   │   └── useAuth.ts
│   ├── stores/
│   │   ├── authStore.ts
│   │   └── filterStore.ts
│   └── utils/
│       ├── cn.ts
│       └── formatters.ts
├── styles/
│   └── globals.css
└── types/
    ├── company.ts
    ├── partnership.ts
    └── user.ts
```

КЛЮЧЕВЫЕ КОМПОНЕНТЫ:

1. COMPANY CARD:
```tsx
'use client';

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Company } from "@/types/company";

export function CompanyCard({ company }: { company: Company }) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex gap-4">
            <img 
              src={company.logo_url} 
              alt={company.name}
              className="w-16 h-16 rounded-lg"
            />
            <div>
              <h3 className="text-xl font-semibold">{company.name}</h3>
              <p className="text-sm text-muted-foreground">
                {company.industry} • {company.headquarters_city}
              </p>
            </div>
          </div>
          <Badge variant="secondary">{company.employees_range}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm mb-4 line-clamp-2">{company.description}</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {company.tech_stack?.slice(0, 5).map(tech => (
            <Badge key={tech} variant="outline">{tech}</Badge>
          ))}
        </div>
        <div className="flex gap-2">
          <Button variant="default" className="flex-1">
            Подробнее
          </Button>
          <Button variant="outline" className="flex-1">
            Найти партнёров
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

2. COMPATIBILITY SCORE:
```tsx
'use client';

import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

export function CompatibilityScore({ score }: { score: number }) {
  const getColor = (score: number) => {
    if (score >= 0.8) return "bg-green-500";
    if (score >= 0.6) return "bg-yellow-500";
    return "bg-red-500";
  };
  
  const getLabel = (score: number) => {
    if (score >= 0.8) return "Отличная";
    if (score >= 0.6) return "Хорошая";
    return "Низкая";
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Совместимость</span>
        <Badge className={getColor(score)}>
          {getLabel(score)} ({Math.round(score * 100)}%)
        </Badge>
      </div>
      <Progress value={score * 100} className={getColor(score)} />
    </div>
  );
}
```

3. REAL-TIME UPDATES (WebSocket):
```tsx
'use client';

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';

export function useRealtimeUpdates() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/ws');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'company.created':
          queryClient.invalidateQueries({ queryKey: ['companies'] });
          break;
        case 'partnership.matched':
          queryClient.invalidateQueries({ queryKey: ['partnerships'] });
          // Show toast notification
          toast.success('Найдено новое партнёрство!');
          break;
      }
    };

    return () => ws.close();
  }, [queryClient]);
}
```

4. DATA FETCHING (Server Components):
```tsx
// app/(dashboard)/companies/page.tsx
import { CompanyCard } from '@/components/companies/CompanyCard';
import { getCompanies } from '@/lib/api/companies';

export default async function CompaniesPage({
  searchParams,
}: {
  searchParams: { industry?: string; page?: string };
}) {
  const companies = await getCompanies({
    industry: searchParams.industry,
    page: Number(searchParams.page) || 1,
  });

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Компании</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {companies.map(company => (
          <CompanyCard key={company.id} company={company} />
        ))}
      </div>
    </div>
  );
}
```

5. AUTHENTICATION (NextAuth):
```ts
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

export const authOptions = {
  providers: [
    CredentialsProvider({
      credentials: {
        email: { type: "email" },
        password: { type: "password" }
      },
      async authorize(credentials) {
        const res = await fetch('http://localhost:8001/auth/login', {
          method: 'POST',
          body: JSON.stringify(credentials),
          headers: { "Content-Type": "application/json" }
        });
        
        const user = await res.json();
        
        if (res.ok && user) {
          return user;
        }
        return null;
      }
    })
  ],
  session: {
    strategy: 'jwt',
  },
  pages: {
    signIn: '/login',
  },
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
```

ТРЕБОВАНИЯ:
- Server Components по умолчанию
- Client Components только где нужна интерактивность
- Streaming с Suspense
- Progressive enhancement
- Responsive design (mobile-first)
- Dark mode поддержка
- Accessibility (ARIA)
- SEO optimization

Создай полное Next.js приложение со всеми компонентами.
```

---

## Промпт №9: DevOps

### Задача
Настроить полный DevOps: CI/CD, Kubernetes, мониторинг.

### Промпт

```markdown
Создай полную DevOps инфраструктуру для платформы ALGORITHMIC ARTS в Yandex Cloud.

КОМПОНЕНТЫ:

1. KUBERNETES MANIFESTS:

**Deployment для каждого микросервиса:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: company-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: company-service
  template:
    metadata:
      labels:
        app: company-service
    spec:
      containers:
      - name: company-service
        image: cr.yandex/algorithmic-arts/company-service:latest
        ports:
        - containerPort: 8003
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8003
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8003
          initialDelaySeconds: 10
          periodSeconds: 5
```

**HPA (Horizontal Pod Autoscaler):**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: company-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: company-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

2. GITHUB ACTIONS CI/CD:

**.github/workflows/ci.yml:**
```yaml
name: CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      working-directory: services/company-service
      run: poetry install
    
    - name: Run linters
      working-directory: services/company-service
      run: |
        poetry run ruff check .
        poetry run mypy src/
    
    - name: Run tests
      working-directory: services/company-service
      run: |
        poetry run pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
```

**.github/workflows/cd.yml:**
```yaml
name: CD

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Login to Yandex Container Registry
      run: |
        echo ${{ secrets.YC_SA_KEY }} | docker login \
          --username json_key \
          --password-stdin \
          cr.yandex
    
    - name: Build and push Docker images
      run: |
        services=(
          "api-gateway"
          "company-service"
          "auth-service"
          "ai-core-service"
        )
        
        for service in "${services[@]}"; do
          docker build -t cr.yandex/algorithmic-arts/$service:${{ github.sha }} \
            ./services/$service
          docker push cr.yandex/algorithmic-arts/$service:${{ github.sha }}
          
          # Tag as latest
          docker tag cr.yandex/algorithmic-arts/$service:${{ github.sha }} \
            cr.yandex/algorithmic-arts/$service:latest
          docker push cr.yandex/algorithmic-arts/$service:latest
        done
    
    - name: Deploy to Kubernetes
      run: |
        yc managed-kubernetes cluster \
          get-credentials algorithmic-arts-cluster \
          --external
        
        kubectl set image deployment/company-service \
          company-service=cr.yandex/algorithmic-arts/company-service:${{ github.sha }} \
          -n production
        
        kubectl rollout status deployment/company-service -n production
```

3. TERRAFORM (Yandex Cloud):

```hcl
# main.tf
terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  zone = "ru-central1-a"
}

# Kubernetes Cluster
resource "yandex_kubernetes_cluster" "algorithmic_arts" {
  name        = "algorithmic-arts-cluster"
  network_id  = yandex_vpc_network.main.id

  master {
    version = "1.28"
    zonal {
      zone      = "ru-central1-a"
      subnet_id = yandex_vpc_subnet.main.id
    }
    public_ip = true
  }

  service_account_id      = yandex_iam_service_account.k8s_sa.id
  node_service_account_id = yandex_iam_service_account.k8s_nodes_sa.id
}

# PostgreSQL Cluster
resource "yandex_mdb_postgresql_cluster" "main" {
  name        = "algorithmic-arts-db"
  environment = "PRODUCTION"
  network_id  = yandex_vpc_network.main.id

  config {
    version = "17"
    resources {
      resource_preset_id = "s2.medium"
      disk_type_id       = "network-ssd"
      disk_size          = 500
    }
  }

  host {
    zone      = "ru-central1-a"
    subnet_id = yandex_vpc_subnet.main.id
  }
  
  host {
    zone      = "ru-central1-b"
    subnet_id = yandex_vpc_subnet.replica.id
    replication_source_name = "algorithmic-arts-db-host-1"
  }
}
```

4. PROMETHEUS + GRAFANA:

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
```

**Grafana Dashboard (JSON):**
- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Request throughput (req/sec)
- Active connections
- Database query time
- Cache hit rate

5. ALERTING (AlertManager):

```yaml
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'telegram'

receivers:
  - name: 'telegram'
    telegram_configs:
      - bot_token: $TELEGRAM_BOT_TOKEN
        chat_id: $TELEGRAM_CHAT_ID
        parse_mode: 'HTML'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']
```

**Alert Rules:**
```yaml
groups:
  - name: services
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate on {{ $labels.service }}"
        description: "Error rate is {{ $value | humanizePercentage }}"
    
    - alert: SlowResponse
      expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "Slow response time on {{ $labels.service }}"
```

ТРЕБОВАНИЯ:
- Multi-stage Docker builds
- K8s secrets для чувствительных данных
- Network policies для изоляции
- Resource quotas по namespace
- Backup стратегия (Velero)
- Disaster recovery plan
- Blue-green deployments

Создай полную DevOps инфраструктуру с мониторингом.
```

---

## 📝 Как использовать промпты

### Последовательность генерации

1. **Промпт №1** → Создаёт структуру проекта, Docker Compose
2. **Промпт №2** → Создаёт схемы БД и миграции
3. **Промпты №3-7** → Создают микросервисы (можно параллельно)
4. **Промпт №8** → Создаёт frontend
5. **Промпт №9** → Настраивает DevOps

### Советы по работе с AI

1. **Используйте по одному промпту за раз**
2. **Проверяйте сгенерированный код** перед следующим промптом
3. **Адаптируйте промпты** под свои нужды
4. **Добавляйте контекст** из предыдущих шагов

### Проверка результата

После каждого промпта:
```bash
# Проверка структуры
ls -la services/company-service/

# Проверка синтаксиса
poetry run ruff check .

# Запуск тестов
poetry run pytest

# Сборка Docker
docker build -t company-service .
```

---

**Последнее обновление:** Февраль 2026  
**Версия:** 3.0
