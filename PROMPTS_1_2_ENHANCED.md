# ALGORITHMIC ARTS — Улучшенные Промпты №1 и №2

**Версия:** 3.1 (Enhanced)  
**Дата:** Февраль 2026  
**Статус:** Production Ready  

> Расширенная версия промптов №1 и №2 из `PROMPTS_FOR_QWEN.md`.  
> Добавлены: полная файловая структура с перечнем каждого файла, конкретные Dockerfile (multi-stage), полный `.env.example`, расширенный Makefile со всеми командами, скрипты генерации секретов. В промпте №2 — SQL DDL со всеми индексами, триггерами и партиционированием, Alembic-миграции с реальным кодом, SQLAlchemy 2.0 (Mapped-синтаксис), ClickHouse-схема и seed-скрипт.

---

## Промпт №1: Инфраструктура (Расширенный)

### Задача
Создать полную инфраструктуру проекта: структуру директорий, Docker Compose, Dockerfile для каждого сервиса, `.env.example`, Makefile, скрипты инициализации.

### Промпт

```markdown
Создай полную production-ready инфраструктуру для микросервисной платформы ALGORITHMIC ARTS.
Python 3.12, Node.js 22, Docker 24+, Docker Compose 2.24+.

═══════════════════════════════════════════════════════════
ЧАСТЬ 1: СТРУКТУРА ПРОЕКТА
═══════════════════════════════════════════════════════════

Создай следующую файловую структуру (все файлы должны быть заполнены):

platform/
├── .env.example                     # Все переменные окружения с комментариями
├── .gitignore
├── .dockerignore
├── Makefile                         # Полный набор команд
├── docker-compose.yml               # Production-конфигурация
├── docker-compose.override.yml      # Dev-overrides (volume mounts, hot reload)
├── docker-compose.test.yml          # CI/CD конфигурация
│
├── services/
│   ├── api-gateway/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── src/main.py
│   ├── auth-service/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── user-service/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── company-service/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── partner-service/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── ai-core-service/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── data-pipeline/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── crm-hub/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── search-service/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── reporting/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── billing/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   └── notification/
│       ├── Dockerfile
│       └── pyproject.toml
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── .env.local.example
│
├── shared/                          # Общий код для всех сервисов
│   ├── __init__.py
│   ├── events.py                    # Kafka producer/consumer base
│   ├── exceptions.py                # Базовые исключения
│   ├── logging.py                   # Structlog конфигурация
│   └── schemas.py                   # Общие Pydantic-схемы
│
├── infra/
│   ├── postgres/
│   │   └── init.sql                 # Расширения + базовые схемы
│   ├── monitoring/
│   │   ├── prometheus.yml
│   │   ├── loki-config.yml
│   │   └── grafana/
│   │       ├── dashboards/
│   │       │   └── overview.json
│   │       └── datasources/
│   │           └── datasources.yml
│   └── kafka/
│       └── topics.sh                # Создание топиков при старте
│
├── scripts/
│   ├── generate_secrets.py          # Генерация JWT-ключей, паролей
│   ├── check_dependencies.sh        # Проверка версий ПО
│   ├── init_project.sh              # Первичная инициализация
│   ├── create_admin.py              # Создание первого администратора
│   └── seed_data.py                 # Загрузка тестовых данных
│
├── ai-agents/
│   ├── __init__.py
│   ├── base_agent.py
│   └── orchestrator.py
│
└── tests/
    ├── conftest.py
    ├── e2e/
    └── load/
        └── api_load_test.js


═══════════════════════════════════════════════════════════
ЧАСТЬ 2: СЕРВИСЫ И ПОРТЫ
═══════════════════════════════════════════════════════════

Сервис              | Порт  | Технология
--------------------|-------|---------------------------
api-gateway         |  80   | FastAPI, Caddy
auth-service        | 8001  | FastAPI
user-service        | 8002  | FastAPI
company-service     | 8003  | FastAPI
partner-service     | 8004  | FastAPI
ai-core-service     | 8005  | FastAPI, LangChain
data-pipeline       | 8006  | FastAPI, Scrapy, Celery
crm-hub             | 8007  | FastAPI
search-service      | 8008  | FastAPI, Elasticsearch
reporting           | 8009  | FastAPI, WeasyPrint
billing             | 8010  | FastAPI
notification        | 8011  | FastAPI, Celery
frontend            | 3000  | Next.js 15
postgres            | 5432  | PostgreSQL 17 + pgvector
redis               | 6379  | Redis Stack 7.4
redis-insight       | 8001  | RedisInsight UI
elasticsearch       | 9200  | Elasticsearch 8.14
kafka               | 9092  | Apache Kafka 3.7
zookeeper           | 2181  | ZooKeeper
minio               | 9000  | MinIO (S3)
minio-console       | 9001  | MinIO Console
clickhouse-http     | 8123  | ClickHouse HTTP API
clickhouse-native   | 9000  | ClickHouse Native
prometheus          | 9090  | Prometheus
grafana             | 3001  | Grafana
loki                | 3100  | Loki
jaeger              | 16686 | Jaeger UI
pgadmin             | 5050  | pgAdmin 4


═══════════════════════════════════════════════════════════
ЧАСТЬ 3: DOCKERFILE (Python-сервис, multi-stage)
═══════════════════════════════════════════════════════════

Создай единый шаблон Dockerfile для всех Python-сервисов:

# ─── Stage 1: Builder ────────────────────────────────────
FROM python:3.12-slim AS builder

RUN pip install poetry==1.8.3

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.in-project true && \
    poetry install --only=main --no-interaction --no-ansi

# ─── Stage 2: Development ────────────────────────────────
FROM python:3.12-slim AS development

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ─── Stage 3: Production ─────────────────────────────────
FROM python:3.12-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаём непривилегированного пользователя
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --chown=appuser:appuser . .

USER appuser

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", "--no-access-log"]


Для frontend (Next.js 15):

# ─── Stage 1: Dependencies ───────────────────────────────
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# ─── Stage 2: Builder ────────────────────────────────────
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ─── Stage 3: Production ─────────────────────────────────
FROM node:22-alpine AS production
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser  --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]


═══════════════════════════════════════════════════════════
ЧАСТЬ 4: .env.example (полный)
═══════════════════════════════════════════════════════════

Создай .env.example с такими секциями и переменными:

# ─── APPLICATION ────────────────────────────────────────────────
APP_ENV=development              # development | staging | production
APP_DEBUG=true
LOG_LEVEL=INFO                   # DEBUG | INFO | WARNING | ERROR
SECRET_KEY=REPLACE_ME            # 64-byte hex

# ─── POSTGRESQL ─────────────────────────────────────────────────
DB_HOST=postgres
DB_PORT=5432
DB_USER=algo_user
DB_PASSWORD=REPLACE_ME
DB_NAME=algorithmic_arts
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# ─── REDIS ──────────────────────────────────────────────────────
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0
REDIS_CACHE_TTL=3600             # Секунды
REDIS_SESSION_TTL=86400

# ─── ELASTICSEARCH ──────────────────────────────────────────────
ELASTICSEARCH_URL=http://elasticsearch:9200
ELASTICSEARCH_INDEX_PREFIX=algo

# ─── KAFKA ──────────────────────────────────────────────────────
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_CONSUMER_GROUP_ID=algo-platform
KAFKA_AUTO_OFFSET_RESET=earliest
KAFKA_MAX_POLL_RECORDS=500

# ─── MINIO ──────────────────────────────────────────────────────
MINIO_ENDPOINT=minio:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=REPLACE_ME
MINIO_BUCKET_UPLOADS=uploads
MINIO_BUCKET_REPORTS=reports
MINIO_BUCKET_BACKUPS=backups

# ─── CLICKHOUSE ─────────────────────────────────────────────────
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=algo_user
CLICKHOUSE_PASSWORD=REPLACE_ME
CLICKHOUSE_DB=analytics

# ─── JWT ─────────────────────────────────────────────────────────
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
# Генерируются автоматически скриптом generate_secrets.py:
# JWT_PRIVATE_KEY=...
# JWT_PUBLIC_KEY=...

# ─── YANDEXGPT ──────────────────────────────────────────────────
YANDEXGPT_API_KEY=REPLACE_ME
YANDEXGPT_FOLDER_ID=REPLACE_ME
YANDEXGPT_MODEL=yandexgpt-pro
YANDEXGPT_TEMPERATURE=0.3
YANDEXGPT_MAX_TOKENS=4000

# ─── GIGACHAT ───────────────────────────────────────────────────
GIGACHAT_API_KEY=REPLACE_ME
GIGACHAT_SCOPE=GIGACHAT_API_CORP
GIGACHAT_MODEL=GigaChat-Pro

# ─── OPENROUTER (fallback) ──────────────────────────────────────
OPENROUTER_API_KEY=REPLACE_ME
OPENROUTER_MODEL=anthropic/claude-sonnet-4-5

# ─── CRM: amoCRM ─────────────────────────────────────────────────
AMOCRM_CLIENT_ID=REPLACE_ME
AMOCRM_CLIENT_SECRET=REPLACE_ME
AMOCRM_REDIRECT_URI=http://localhost/api/v1/crm/amocrm/callback

# ─── CRM: Битрикс24 ─────────────────────────────────────────────
BITRIX24_CLIENT_ID=REPLACE_ME
BITRIX24_CLIENT_SECRET=REPLACE_ME
BITRIX24_REDIRECT_URI=http://localhost/api/v1/crm/bitrix/callback

# ─── EMAIL (SMTP) ────────────────────────────────────────────────
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
SMTP_USER=noreply@algorithmic-arts.ru
SMTP_PASSWORD=REPLACE_ME
SMTP_FROM_NAME=ALGORITHMIC ARTS

# ─── TELEGRAM ───────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN=REPLACE_ME
TELEGRAM_WEBHOOK_URL=https://api.algorithmic-arts.ru/webhooks/telegram

# ─── PAYMENTS: ЮKassa ───────────────────────────────────────────
YUKASSA_SHOP_ID=REPLACE_ME
YUKASSA_SECRET_KEY=REPLACE_ME
YUKASSA_RETURN_URL=https://algorithmic-arts.ru/billing/success

# ─── MONITORING ─────────────────────────────────────────────────
GRAFANA_PASSWORD=REPLACE_ME
PGADMIN_EMAIL=admin@algorithmic-arts.ru
PGADMIN_PASSWORD=REPLACE_ME

# ─── FRONTEND ───────────────────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost/ws
NEXT_PUBLIC_APP_NAME=ALGORITHMIC ARTS
NEXT_PUBLIC_SENTRY_DSN=


═══════════════════════════════════════════════════════════
ЧАСТЬ 5: MAKEFILE (расширенный)
═══════════════════════════════════════════════════════════

.PHONY: help setup start stop restart logs test clean migrate lint build

# ─── Утилиты ───────────────────────────────────────────────────
help:  ## Показать список команд
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
	    {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ─── Настройка проекта ──────────────────────────────────────────
setup: ## Первичная инициализация проекта
	@echo "🚀 Инициализация ALGORITHMIC ARTS..."
	cp -n .env.example .env || true
	python scripts/generate_secrets.py >> .env
	cp -n frontend/.env.local.example frontend/.env.local || true
	@echo "✅ Настройка завершена. Отредактируйте .env перед запуском."

# ─── Docker ─────────────────────────────────────────────────────
build: ## Пересобрать Docker-образы
	docker compose build --no-cache

start: ## Запустить все сервисы
	docker compose up -d
	@echo "⏳ Ожидание готовности... (30 сек)"
	sleep 30
	$(MAKE) migrate
	@echo "✅ Платформа запущена: http://localhost:3000"

start-infra: ## Запустить только инфраструктуру (БД, Kafka, Redis)
	docker compose up -d postgres redis elasticsearch kafka zookeeper minio clickhouse

stop: ## Остановить все сервисы
	docker compose down

restart: ## Перезапустить все сервисы
	docker compose restart

restart-svc: ## Перезапустить конкретный сервис: make restart-svc SVC=company-service
	docker compose restart $(SVC)

logs: ## Логи всех сервисов (следить)
	docker compose logs -f

logs-svc: ## Логи конкретного сервиса: make logs-svc SVC=auth-service
	docker compose logs -f $(SVC)

ps: ## Статус всех контейнеров
	docker compose ps

# ─── Миграции ───────────────────────────────────────────────────
migrate: ## Применить все миграции
	@for svc in auth-service user-service company-service partner-service billing; do \
	    echo "  → Миграция $$svc..."; \
	    docker compose exec $$svc alembic upgrade head; \
	done

migrate-svc: ## Мигрировать конкретный сервис: make migrate-svc SVC=company-service
	docker compose exec $(SVC) alembic upgrade head

rollback: ## Откатить последнюю миграцию: make rollback SVC=company-service
	docker compose exec $(SVC) alembic downgrade -1

migration-new: ## Создать новую миграцию: make migration-new SVC=company-service MSG="add_index"
	docker compose exec $(SVC) alembic revision --autogenerate -m "$(MSG)"

# ─── Тесты ──────────────────────────────────────────────────────
test: ## Запустить все тесты
	@for svc in auth-service user-service company-service partner-service; do \
	    echo "  → Тестирование $$svc..."; \
	    docker compose exec $$svc poetry run pytest tests/ -v --cov=src --cov-report=term-missing; \
	done
	cd frontend && npm test

test-svc: ## Тестировать конкретный сервис: make test-svc SVC=auth-service
	docker compose exec $(SVC) poetry run pytest tests/ -v --cov=src

test-coverage: ## Отчёт о покрытии (HTML): make test-coverage SVC=company-service
	docker compose exec $(SVC) poetry run pytest --cov=src --cov-report=html
	@echo "Откройте: services/$(SVC)/htmlcov/index.html"

test-load: ## Нагрузочное тестирование
	k6 run tests/load/api_load_test.js

# ─── Shell доступ ────────────────────────────────────────────────
shell-db: ## PostgreSQL shell
	docker compose exec postgres psql -U algo_user -d algorithmic_arts

shell-redis: ## Redis CLI
	docker compose exec redis redis-cli

shell-svc: ## Shell сервиса: make shell-svc SVC=company-service
	docker compose exec $(SVC) bash

# ─── Данные ──────────────────────────────────────────────────────
seed: ## Загрузить тестовые данные (100 компаний)
	docker compose exec data-pipeline python scripts/seed_data.py --count=100

create-admin: ## Создать первого администратора
	docker compose exec api-gateway python scripts/create_admin.py

# ─── Линтинг ─────────────────────────────────────────────────────
lint: ## Проверить стиль кода
	@for svc in auth-service user-service company-service partner-service; do \
	    docker compose exec $$svc poetry run ruff check src/ tests/; \
	    docker compose exec $$svc poetry run mypy src/; \
	done
	cd frontend && npm run lint

format: ## Отформатировать код
	@for svc in auth-service user-service company-service partner-service; do \
	    docker compose exec $$svc poetry run ruff format src/ tests/; \
	done

# ─── Очистка ─────────────────────────────────────────────────────
clean: ## Остановить и удалить все контейнеры и тома
	docker compose down -v --remove-orphans
	docker system prune -f

clean-images: ## Удалить собранные образы
	docker compose down --rmi local


═══════════════════════════════════════════════════════════
ЧАСТЬ 6: СКРИПТЫ
═══════════════════════════════════════════════════════════

## scripts/generate_secrets.py:

#!/usr/bin/env python3
"""Генерация криптографически стойких секретов для .env"""

import secrets
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def generate_rsa_key_pair():
    """Генерирует пару RSA-ключей для RS256 JWT."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return private_pem, public_pem


def main():
    # Случайные пароли для БД
    print(f"DB_PASSWORD={secrets.token_urlsafe(32)}")
    print(f"CLICKHOUSE_PASSWORD={secrets.token_urlsafe(32)}")
    print(f"MINIO_ROOT_PASSWORD={secrets.token_urlsafe(32)}")
    print(f"SECRET_KEY={secrets.token_hex(64)}")
    print(f"GRAFANA_PASSWORD={secrets.token_urlsafe(16)}")
    print(f"PGADMIN_PASSWORD={secrets.token_urlsafe(16)}")

    # RSA ключи для JWT
    private_pem, public_pem = generate_rsa_key_pair()
    # Кодируем в base64 для удобства хранения в .env
    private_b64 = base64.b64encode(private_pem.encode()).decode()
    public_b64  = base64.b64encode(public_pem.encode()).decode()
    print(f"JWT_PRIVATE_KEY={private_b64}")
    print(f"JWT_PUBLIC_KEY={public_b64}")

if __name__ == "__main__":
    main()


## scripts/check_dependencies.sh:

#!/bin/bash
set -e
ERRORS=0

check_version() {
    local tool=$1
    local required=$2
    local actual=$($3 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+')

    if [ -z "$actual" ]; then
        echo "❌ $tool не найден"
        ERRORS=$((ERRORS+1))
    else
        echo "✅ $tool $actual (требуется >= $required)"
    fi
}

echo "🔍 Проверка зависимостей ALGORITHMIC ARTS..."
check_version "Docker"         "24.0" "docker --version"
check_version "Docker Compose" "2.24" "docker compose version"
check_version "Python"         "3.12" "python3 --version"
check_version "Node.js"        "22.0" "node --version"
check_version "Git"            "2.40" "git --version"

[ $ERRORS -eq 0 ] && echo "✅ Все зависимости в порядке!" \
                  || echo "❌ Найдено ошибок: $ERRORS. Установите недостающие компоненты."
exit $ERRORS


## infra/postgres/init.sql:

-- Расширения PostgreSQL 17
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_cron";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Citus (шардирование — только если включён)
-- CREATE EXTENSION IF NOT EXISTS "citus";

-- Shared триггер для auto-update updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Макрос для создания триггера на таблицу
-- Использование: SELECT create_updated_at_trigger('companies');
CREATE OR REPLACE FUNCTION create_updated_at_trigger(table_name TEXT)
RETURNS void AS $$
BEGIN
    EXECUTE format(
        'CREATE TRIGGER set_updated_at
         BEFORE UPDATE ON %I
         FOR EACH ROW EXECUTE FUNCTION set_updated_at()',
        table_name
    );
END;
$$ LANGUAGE plpgsql;


## infra/kafka/topics.sh:

#!/bin/bash
# Создание всех Kafka топиков при первом запуске
KAFKA="kafka:9092"
PARTITIONS=3
REPLICATION=1

create_topic() {
    kafka-topics.sh --create \
        --bootstrap-server $KAFKA \
        --topic $1 \
        --partitions $PARTITIONS \
        --replication-factor $REPLICATION \
        --if-not-exists
}

echo "🔧 Создание Kafka топиков..."

# Company domain
create_topic "company.created"
create_topic "company.updated"
create_topic "company.enriched"
create_topic "company.deleted"

# Partnership domain
create_topic "partnership.matched"
create_topic "partnership.status_changed"
create_topic "partnership.deal_closed"

# User domain
create_topic "user.created"
create_topic "user.updated"
create_topic "user.login_failed"

# Billing domain
create_topic "billing.subscription_created"
create_topic "billing.subscription_changed"
create_topic "billing.payment_succeeded"
create_topic "billing.payment_failed"

# AI domain
create_topic "ai.analysis.queue"
create_topic "ai.analysis.results"

# CRM / Notifications
create_topic "crm.sync.requested"
create_topic "notification.events"

echo "✅ Топики созданы"

ОБЩИЕ ТРЕБОВАНИЯ:
- docker-compose.yml: healthcheck для каждого сервиса, depends_on с condition
- docker-compose.override.yml: volume-маунты для hot reload в dev-режиме
- shared/logging.py: structlog с JSON-форматом, request_id в контексте
- shared/events.py: базовый KafkaProducer и KafkaConsumer с retry-логикой
- Все секреты — только через переменные окружения, не хардкодить

Создай все файлы, включая заглушки src/main.py для каждого сервиса с /health и /metrics.
```

---

## Промпт №2: Базы данных (Расширенный)

### Задача
Создать все схемы PostgreSQL, Alembic-миграции, SQLAlchemy 2.0 модели, ClickHouse-схему и seed-скрипт.

### Промпт

```markdown
Создай полные схемы баз данных для платформы ALGORITHMIC ARTS.
PostgreSQL 17, pgvector 0.7+, SQLAlchemy 2.0 (async + Mapped), Alembic 1.14.

═══════════════════════════════════════════════════════════
ЧАСТЬ 1: SQL DDL — AUTH DATABASE
═══════════════════════════════════════════════════════════

-- Enum типы
CREATE TYPE user_role AS ENUM ('free_user', 'paid_user', 'company_admin', 'platform_admin');
CREATE TYPE oauth_provider AS ENUM ('yandex', 'google', 'vk');

-- Таблица пользователей
CREATE TABLE users (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    email               VARCHAR(255)    NOT NULL UNIQUE,
    password_hash       VARCHAR(72)     NOT NULL,           -- bcrypt, cost 12
    full_name           VARCHAR(255)    NOT NULL,
    company_name        VARCHAR(255),
    role                user_role       NOT NULL DEFAULT 'free_user',
    is_active           BOOLEAN         NOT NULL DEFAULT FALSE,
    is_verified         BOOLEAN         NOT NULL DEFAULT FALSE,
    totp_secret         VARCHAR(32),                        -- NULL = 2FA отключена
    totp_enabled        BOOLEAN         NOT NULL DEFAULT FALSE,
    last_login_at       TIMESTAMPTZ,
    failed_login_count  INTEGER         NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
);

-- Индексы users
CREATE INDEX idx_users_email         ON users (email)      WHERE deleted_at IS NULL;
CREATE INDEX idx_users_role          ON users (role)       WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at    ON users (created_at DESC);
SELECT create_updated_at_trigger('users');

-- Refresh-токены (хранятся зашифрованными)
CREATE TABLE refresh_tokens (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(64) NOT NULL UNIQUE,            -- SHA-256 от токена
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ
);

CREATE INDEX idx_refresh_tokens_user_id    ON refresh_tokens (user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens (expires_at)
    WHERE revoked_at IS NULL;

-- OAuth-подключения
CREATE TABLE oauth_connections (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID            NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider        oauth_provider  NOT NULL,
    external_id     VARCHAR(255)    NOT NULL,
    access_token    TEXT,
    refresh_token   TEXT,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (provider, external_id)
);

CREATE INDEX idx_oauth_user_id ON oauth_connections (user_id);
SELECT create_updated_at_trigger('oauth_connections');

-- Email верификация / сброс пароля
CREATE TABLE verification_tokens (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(64) NOT NULL UNIQUE,                -- криптографически случайный
    purpose     VARCHAR(32) NOT NULL,                       -- 'email_verify' | 'password_reset'
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_verification_tokens_token   ON verification_tokens (token) WHERE used_at IS NULL;
CREATE INDEX idx_verification_tokens_user_id ON verification_tokens (user_id);

-- pg_cron: очистка просроченных токенов каждый час
SELECT cron.schedule('cleanup-expired-tokens', '0 * * * *',
    $$DELETE FROM verification_tokens WHERE expires_at < NOW()$$);
SELECT cron.schedule('cleanup-refresh-tokens', '30 * * * *',
    $$DELETE FROM refresh_tokens WHERE expires_at < NOW() AND revoked_at IS NOT NULL$$);


═══════════════════════════════════════════════════════════
ЧАСТЬ 2: SQL DDL — COMPANY DATABASE
═══════════════════════════════════════════════════════════

-- Enum типы
CREATE TYPE funding_stage AS ENUM (
    'pre_seed', 'seed', 'series_a', 'series_b', 'series_c',
    'series_d_plus', 'ipo', 'bootstrapped', 'unknown'
);
CREATE TYPE employees_range AS ENUM (
    '1-10', '11-50', '51-200', '201-500', '500+'
);
CREATE TYPE business_model AS ENUM (
    'b2b', 'b2c', 'b2b2c', 'marketplace', 'platform', 'other'
);

-- Основная таблица компаний
CREATE TABLE companies (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(255)    NOT NULL,
    slug                VARCHAR(255)    NOT NULL UNIQUE,    -- URL-friendly идентификатор
    description         TEXT,
    website             VARCHAR(500),
    logo_url            VARCHAR(500),
    industry            VARCHAR(100)    NOT NULL,
    sub_industries      TEXT[]          NOT NULL DEFAULT '{}',
    business_model      business_model,
    founded_year        SMALLINT        CHECK (founded_year BETWEEN 1900 AND 2030),
    headquarters_country VARCHAR(10)    NOT NULL DEFAULT 'RU',
    headquarters_city   VARCHAR(100),
    employees_count     INTEGER         CHECK (employees_count > 0),
    employees_range     employees_range,
    funding_total       BIGINT,                             -- в копейках
    funding_currency    VARCHAR(3)      NOT NULL DEFAULT 'RUB',
    funding_stage       funding_stage   DEFAULT 'unknown',
    last_funding_date   DATE,
    inn                 VARCHAR(12)     UNIQUE,             -- ИНН 10 или 12 цифр
    ogrn                VARCHAR(15)     UNIQUE,             -- ОГРН 13 или 15 цифр
    kpp                 VARCHAR(9),
    legal_name          VARCHAR(500),
    tech_stack          JSONB           NOT NULL DEFAULT '{}',
    integrations        TEXT[]          NOT NULL DEFAULT '{}',
    api_available       BOOLEAN         NOT NULL DEFAULT FALSE,
    ai_summary          TEXT,
    ai_tags             TEXT[]          NOT NULL DEFAULT '{}',
    embedding           VECTOR(768),                        -- paraphrase-multilingual-mpnet
    is_verified         BOOLEAN         NOT NULL DEFAULT FALSE,
    view_count          INTEGER         NOT NULL DEFAULT 0,
    source_url          VARCHAR(500),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
);

-- Индексы companies
CREATE INDEX idx_companies_industry     ON companies (industry) WHERE deleted_at IS NULL;
CREATE INDEX idx_companies_country_city ON companies (headquarters_country, headquarters_city)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_companies_funding      ON companies (funding_stage) WHERE deleted_at IS NULL;
CREATE INDEX idx_companies_founded      ON companies (founded_year)  WHERE deleted_at IS NULL;
CREATE INDEX idx_companies_inn          ON companies (inn)           WHERE inn IS NOT NULL;

-- GIN-индексы для массивов и JSONB
CREATE INDEX idx_companies_sub_industries ON companies USING GIN (sub_industries);
CREATE INDEX idx_companies_tech_stack     ON companies USING GIN (tech_stack);
CREATE INDEX idx_companies_integrations   ON companies USING GIN (integrations);
CREATE INDEX idx_companies_ai_tags        ON companies USING GIN (ai_tags);

-- IVFFlat-индекс для pgvector (cosine distance)
-- Значение lists: sqrt(кол-во строк). Для 5000 строк ≈ 70
CREATE INDEX idx_companies_embedding ON companies
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)
    WHERE embedding IS NOT NULL;

SELECT create_updated_at_trigger('companies');

-- История обновлений компании
CREATE TABLE company_updates (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    update_type VARCHAR(50) NOT NULL,   -- 'news' | 'funding' | 'team' | 'product'
    title       VARCHAR(500),
    content     TEXT,
    source_url  VARCHAR(500),
    published_at TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (published_at);

-- Создаём партиции по кварталам 2025-2027
CREATE TABLE company_updates_2025_q1 PARTITION OF company_updates
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE company_updates_2025_q2 PARTITION OF company_updates
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE company_updates_2025_q3 PARTITION OF company_updates
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE company_updates_2025_q4 PARTITION OF company_updates
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
CREATE TABLE company_updates_2026_q1 PARTITION OF company_updates
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
CREATE TABLE company_updates_2026_q2 PARTITION OF company_updates
    FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');

CREATE INDEX idx_company_updates_company_id
    ON company_updates (company_id, published_at DESC);

-- Метрики компании
CREATE TABLE company_metrics (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    metric_name     VARCHAR(100) NOT NULL,  -- 'mrr_rub' | 'employees_count' | 'website_visits'
    metric_value    NUMERIC(20,4) NOT NULL,
    measured_at     TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (measured_at);

CREATE TABLE company_metrics_2025 PARTITION OF company_metrics
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE company_metrics_2026 PARTITION OF company_metrics
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE INDEX idx_company_metrics_company_metric
    ON company_metrics (company_id, metric_name, measured_at DESC);

-- Event Store для Company Aggregate (Event Sourcing)
CREATE TABLE company_events (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID        NOT NULL,
    event_type      VARCHAR(100) NOT NULL,
    event_version   INTEGER     NOT NULL,
    payload         JSONB       NOT NULL,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (company_id, event_version)
);

CREATE INDEX idx_company_events_company_version
    ON company_events (company_id, event_version ASC);


═══════════════════════════════════════════════════════════
ЧАСТЬ 3: SQL DDL — PARTNERSHIP DATABASE
═══════════════════════════════════════════════════════════

CREATE TYPE partnership_status AS ENUM (
    'suggested',    -- Автоматически найдено системой
    'reviewed',     -- Пользователь просмотрел
    'interested',   -- Пользователь заинтересован
    'contacted',    -- Отправлено outreach письмо
    'responded',    -- Получен ответ
    'negotiating',  -- Идут переговоры
    'active',       -- Партнёрство заключено
    'closed',       -- Завершено
    'rejected'      -- Отклонено
);

CREATE TYPE analysis_method AS ENUM (
    'auto_vector_scoring',  -- Автоматический: vector search + scoring
    'user_requested',       -- Инициировано пользователем
    'ai_deep_analysis'      -- Глубокий AI-анализ (LLM)
);

CREATE TABLE partnerships (
    id                          UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    company_a_id                UUID                NOT NULL REFERENCES companies(id),
    company_b_id                UUID                NOT NULL REFERENCES companies(id),
    compatibility_score         NUMERIC(5,4)        NOT NULL    -- 0.0000 - 1.0000
                                    CHECK (compatibility_score BETWEEN 0 AND 1),
    tech_compatibility_score    NUMERIC(5,4),
    market_overlap_score        NUMERIC(5,4),
    size_match_score            NUMERIC(5,4),
    geo_proximity_score         NUMERIC(5,4),
    no_competition_score        NUMERIC(5,4),
    complementarity_score       NUMERIC(5,4),
    match_reasons               TEXT[]              NOT NULL DEFAULT '{}',
    synergy_areas               TEXT[]              NOT NULL DEFAULT '{}',
    recommended_type            VARCHAR(50),                    -- 'integration' | 'reseller' | 'co-development'
    analysis_method             analysis_method     NOT NULL DEFAULT 'auto_vector_scoring',
    analyzed_by_agent           VARCHAR(100),
    ai_explanation              TEXT,
    status                      partnership_status  NOT NULL DEFAULT 'suggested',
    viewed_at                   TIMESTAMPTZ,
    contacted_at                TIMESTAMPTZ,
    responded_at                TIMESTAMPTZ,
    partnership_started_at      TIMESTAMPTZ,
    deal_value                  BIGINT,                         -- в копейках
    revenue_generated           BIGINT,                         -- в копейках
    notes                       TEXT,
    created_at                  TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ         NOT NULL DEFAULT NOW(),

    -- Уникальность: пара компаний встречается один раз (независимо от порядка)
    CONSTRAINT unique_company_pair CHECK (company_a_id < company_b_id),
    UNIQUE (company_a_id, company_b_id)
);

CREATE INDEX idx_partnerships_company_a      ON partnerships (company_a_id, compatibility_score DESC);
CREATE INDEX idx_partnerships_company_b      ON partnerships (company_b_id, compatibility_score DESC);
CREATE INDEX idx_partnerships_status         ON partnerships (status, created_at DESC);
CREATE INDEX idx_partnerships_high_score     ON partnerships (compatibility_score DESC)
    WHERE status = 'suggested';
SELECT create_updated_at_trigger('partnerships');

-- Outreach-сообщения
CREATE TABLE outreach_messages (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    partnership_id      UUID        NOT NULL REFERENCES partnerships(id) ON DELETE CASCADE,
    sent_by_user_id     UUID        REFERENCES users(id),       -- NULL = авто
    channel             VARCHAR(20) NOT NULL DEFAULT 'email',   -- 'email' | 'telegram'
    message_text        TEXT        NOT NULL,
    sent_at             TIMESTAMPTZ,
    delivery_status     VARCHAR(20) DEFAULT 'pending',          -- 'pending' | 'sent' | 'failed'
    response_received   BOOLEAN     NOT NULL DEFAULT FALSE,
    response_text       TEXT,
    responded_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_outreach_partnership_id ON outreach_messages (partnership_id, sent_at DESC);


═══════════════════════════════════════════════════════════
ЧАСТЬ 4: SQL DDL — CRM И BILLING DATABASES
═══════════════════════════════════════════════════════════

-- CRM-подключения
CREATE TYPE crm_type AS ENUM ('amocrm', 'bitrix24', 'salesforce', 'hubspot');
CREATE TYPE sync_direction AS ENUM ('to_crm', 'from_crm', 'bidirectional');
CREATE TYPE sync_status AS ENUM ('pending', 'success', 'failed', 'partial');

CREATE TABLE crm_connections (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    crm_type        crm_type    NOT NULL,
    access_token    TEXT        NOT NULL,           -- AES-256 зашифрован
    refresh_token   TEXT,                           -- AES-256 зашифрован
    expires_at      TIMESTAMPTZ,
    account_subdomain VARCHAR(100),                 -- для amoCRM, Битрикс24
    account_id      VARCHAR(100),
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    last_sync_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, crm_type)
);

CREATE INDEX idx_crm_connections_user_id ON crm_connections (user_id);
SELECT create_updated_at_trigger('crm_connections');

CREATE TABLE crm_sync_logs (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id   UUID            NOT NULL REFERENCES crm_connections(id) ON DELETE CASCADE,
    direction       sync_direction  NOT NULL,
    entity_type     VARCHAR(50)     NOT NULL,   -- 'company' | 'contact' | 'deal'
    entity_id       UUID,
    external_id     VARCHAR(255),               -- ID в CRM-системе
    status          sync_status     NOT NULL DEFAULT 'pending',
    error_message   TEXT,
    records_synced  INTEGER         DEFAULT 0,
    synced_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_crm_sync_logs_connection ON crm_sync_logs (connection_id, synced_at DESC);

-- Billing
CREATE TYPE subscription_plan AS ENUM ('starter', 'growth', 'scale', 'enterprise');
CREATE TYPE subscription_status AS ENUM ('active', 'trialing', 'past_due', 'cancelled', 'expired');
CREATE TYPE payment_status AS ENUM ('pending', 'succeeded', 'failed', 'refunded');
CREATE TYPE payment_method AS ENUM ('card', 'bank_transfer', 'sbp', 'crypto');

CREATE TABLE subscriptions (
    id                      UUID                    PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID                    NOT NULL REFERENCES users(id),
    plan                    subscription_plan       NOT NULL DEFAULT 'starter',
    status                  subscription_status     NOT NULL DEFAULT 'trialing',
    trial_ends_at           TIMESTAMPTZ,
    current_period_start    TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    current_period_end      TIMESTAMPTZ             NOT NULL,
    cancel_at_period_end    BOOLEAN                 NOT NULL DEFAULT FALSE,
    cancelled_at            TIMESTAMPTZ,
    external_subscription_id VARCHAR(255),          -- ID в ЮKassa
    created_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_subscriptions_user_active
    ON subscriptions (user_id) WHERE status IN ('active', 'trialing', 'past_due');
SELECT create_updated_at_trigger('subscriptions');

CREATE TABLE payments (
    id                      UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id         UUID                NOT NULL REFERENCES subscriptions(id),
    user_id                 UUID                NOT NULL REFERENCES users(id),
    amount                  BIGINT              NOT NULL CHECK (amount > 0),  -- в копейках
    currency                VARCHAR(3)          NOT NULL DEFAULT 'RUB',
    status                  payment_status      NOT NULL DEFAULT 'pending',
    payment_method          payment_method,
    external_payment_id     VARCHAR(255)        UNIQUE,
    description             VARCHAR(500),
    failure_reason          TEXT,
    paid_at                 TIMESTAMPTZ,
    created_at              TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_user_id        ON payments (user_id, created_at DESC);
CREATE INDEX idx_payments_subscription   ON payments (subscription_id);
CREATE INDEX idx_payments_status         ON payments (status) WHERE status = 'pending';


═══════════════════════════════════════════════════════════
ЧАСТЬ 5: CLICKHOUSE SCHEMA (аналитика)
═══════════════════════════════════════════════════════════

-- user_events: все действия пользователей
CREATE TABLE analytics.user_events (
    event_id        UUID,
    user_id         UUID,
    session_id      String,
    event_type      LowCardinality(String),  -- 'search', 'view_company', 'request_contact'
    properties      String,                  -- JSON строка
    page_url        String,
    referrer        String,
    ip_address      IPv4,
    user_agent      String,
    occurred_at     DateTime64(3, 'Europe/Moscow')
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(occurred_at)
ORDER BY (user_id, occurred_at)
TTL occurred_at + INTERVAL 90 DAY;

-- search_queries: все поисковые запросы
CREATE TABLE analytics.search_queries (
    query_id        UUID,
    user_id         UUID,
    query_text      String,
    filters         String,                  -- JSON
    results_count   UInt32,
    clicked_ids     Array(UUID),
    response_ms     UInt32,
    occurred_at     DateTime64(3, 'Europe/Moscow')
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(occurred_at)
ORDER BY (occurred_at, user_id)
TTL occurred_at + INTERVAL 180 DAY;

-- partnership_funnel: воронка партнёрств
CREATE TABLE analytics.partnership_funnel (
    partnership_id  UUID,
    company_a_id    UUID,
    company_b_id    UUID,
    score           Float32,
    suggested_at    DateTime64(3, 'Europe/Moscow'),
    viewed_at       Nullable(DateTime64(3)),
    contacted_at    Nullable(DateTime64(3)),
    responded_at    Nullable(DateTime64(3)),
    deal_closed_at  Nullable(DateTime64(3)),
    deal_value_rub  Nullable(Int64)
) ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(suggested_at)
ORDER BY partnership_id;

-- Kafka → ClickHouse интеграция через Kafka Engine
CREATE TABLE analytics.kafka_events_queue (
    raw JSON
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list  = 'user.created,company.created,partnership.matched',
    kafka_group_name  = 'clickhouse-analytics',
    kafka_format      = 'JSONEachRow';


═══════════════════════════════════════════════════════════
ЧАСТЬ 6: ALEMBIC МИГРАЦИЯ (пример)
═══════════════════════════════════════════════════════════

## services/company-service/alembic/versions/0001_companies_table.py:

"""Create companies tables

Revision ID: 0001
Revises:
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Включаем расширения
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pgvector\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pg_cron\"")

    # Создаём функцию set_updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    # Enum типы
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE funding_stage AS ENUM (
                'pre_seed','seed','series_a','series_b','series_c',
                'series_d_plus','ipo','bootstrapped','unknown'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE employees_range AS ENUM (
                '1-10','11-50','51-200','201-500','500+'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)

    # Таблица companies
    op.create_table(
        'companies',
        sa.Column('id',           sa.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('name',         sa.String(255), nullable=False),
        sa.Column('slug',         sa.String(255), nullable=False, unique=True),
        sa.Column('description',  sa.Text),
        sa.Column('website',      sa.String(500)),
        sa.Column('industry',     sa.String(100), nullable=False),
        sa.Column('sub_industries', sa.ARRAY(sa.Text), nullable=False,
                  server_default='{}'),
        sa.Column('founded_year', sa.SmallInteger,
                  sa.CheckConstraint('founded_year BETWEEN 1900 AND 2030')),
        sa.Column('headquarters_country', sa.String(10), nullable=False,
                  server_default='RU'),
        sa.Column('headquarters_city',    sa.String(100)),
        sa.Column('employees_range', sa.Enum('1-10','11-50','51-200','201-500','500+',
                  name='employees_range', create_type=False)),
        sa.Column('funding_total',    sa.BigInteger),
        sa.Column('funding_currency', sa.String(3),  nullable=False,
                  server_default='RUB'),
        sa.Column('funding_stage', sa.Enum('pre_seed','seed','series_a','series_b',
                  'series_c','series_d_plus','ipo','bootstrapped','unknown',
                  name='funding_stage', create_type=False), server_default='unknown'),
        sa.Column('inn',          sa.String(12), unique=True),
        sa.Column('ogrn',         sa.String(15), unique=True),
        sa.Column('legal_name',   sa.String(500)),
        sa.Column('tech_stack',   sa.JSON,        nullable=False, server_default='{}'),
        sa.Column('integrations', sa.ARRAY(sa.Text), nullable=False, server_default='{}'),
        sa.Column('api_available',sa.Boolean,     nullable=False, server_default='false'),
        sa.Column('ai_summary',   sa.Text),
        sa.Column('ai_tags',      sa.ARRAY(sa.Text), nullable=False, server_default='{}'),
        sa.Column('embedding',    Vector(768)),
        sa.Column('is_verified',  sa.Boolean,     nullable=False, server_default='false'),
        sa.Column('view_count',   sa.Integer,     nullable=False, server_default='0'),
        sa.Column('created_at',   sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at',   sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('deleted_at',   sa.DateTime(timezone=True)),
    )

    # Индексы
    op.create_index('idx_companies_industry',
        'companies', ['industry'],
        postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_companies_sub_industries',
        'companies', ['sub_industries'],
        postgresql_using='gin')
    op.create_index('idx_companies_tech_stack',
        'companies', [sa.text("tech_stack")],
        postgresql_using='gin')
    op.create_index('idx_companies_ai_tags',
        'companies', ['ai_tags'],
        postgresql_using='gin')

    # IVFFlat vector index
    op.execute("""
        CREATE INDEX idx_companies_embedding
        ON companies
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        WHERE embedding IS NOT NULL;
    """)

    # Триггер updated_at
    op.execute("""
        CREATE TRIGGER set_updated_at
        BEFORE UPDATE ON companies
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)


def downgrade() -> None:
    op.drop_table('companies')
    op.execute("DROP TYPE IF EXISTS funding_stage")
    op.execute("DROP TYPE IF EXISTS employees_range")


═══════════════════════════════════════════════════════════
ЧАСТЬ 7: SQLALCHEMY 2.0 МОДЕЛИ
═══════════════════════════════════════════════════════════

## services/company-service/src/infrastructure/models.py:

from datetime import datetime, date
from uuid import UUID, uuid4
from typing import Any
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    pass


class CompanyORM(Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    slug: Mapped[str] = mapped_column(sa.String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(sa.Text)
    website: Mapped[str | None] = mapped_column(sa.String(500))
    industry: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    sub_industries: Mapped[list[str]] = mapped_column(
        ARRAY(sa.Text), nullable=False, server_default=sa.text("'{}'::text[]")
    )
    founded_year: Mapped[int | None] = mapped_column(sa.SmallInteger)
    headquarters_country: Mapped[str] = mapped_column(
        sa.String(10), nullable=False, server_default="RU"
    )
    headquarters_city: Mapped[str | None] = mapped_column(sa.String(100))
    employees_range: Mapped[str | None] = mapped_column(
        sa.Enum("1-10", "11-50", "51-200", "201-500", "500+", name="employees_range")
    )
    funding_total: Mapped[int | None] = mapped_column(sa.BigInteger)   # в копейках
    funding_currency: Mapped[str] = mapped_column(
        sa.String(3), nullable=False, server_default="RUB"
    )
    funding_stage: Mapped[str] = mapped_column(
        sa.Enum("pre_seed", "seed", "series_a", "series_b", "series_c",
                "series_d_plus", "ipo", "bootstrapped", "unknown",
                name="funding_stage"),
        server_default="unknown"
    )
    inn: Mapped[str | None] = mapped_column(sa.String(12), unique=True)
    ogrn: Mapped[str | None] = mapped_column(sa.String(15), unique=True)
    legal_name: Mapped[str | None] = mapped_column(sa.String(500))
    tech_stack: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")
    )
    integrations: Mapped[list[str]] = mapped_column(
        ARRAY(sa.Text), nullable=False, server_default=sa.text("'{}'::text[]")
    )
    api_available: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default="false"
    )
    ai_summary: Mapped[str | None] = mapped_column(sa.Text)
    ai_tags: Mapped[list[str]] = mapped_column(
        ARRAY(sa.Text), nullable=False, server_default=sa.text("'{}'::text[]")
    )
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768))
    is_verified: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default="false"
    )
    view_count: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(),
        onupdate=sa.func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    __table_args__ = (
        sa.CheckConstraint("founded_year BETWEEN 1900 AND 2030", name="ck_founded_year"),
    )


## services/auth-service/src/infrastructure/models.py:

class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(
        sa.String(255), nullable=False, unique=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(sa.String(72), nullable=False)
    full_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    company_name: Mapped[str | None] = mapped_column(sa.String(255))
    role: Mapped[str] = mapped_column(
        sa.Enum("free_user", "paid_user", "company_admin", "platform_admin",
                name="user_role"),
        nullable=False, server_default="free_user"
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default="false"
    )
    is_verified: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default="false"
    )
    totp_secret: Mapped[str | None] = mapped_column(sa.String(32))
    totp_enabled: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default="false"
    )
    last_login_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    failed_login_count: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(),
        onupdate=sa.func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))


class RefreshTokenORM(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(sa.String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    revoked_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))


═══════════════════════════════════════════════════════════
ЧАСТЬ 8: SEED DATA SCRIPT
═══════════════════════════════════════════════════════════

## scripts/seed_data.py:

#!/usr/bin/env python3
"""
Загрузка тестовых данных: компании, пользователи, партнёрства.
Использование: python seed_data.py --count=100
"""

import asyncio
import argparse
import random
from uuid import uuid4
from datetime import datetime, timedelta
from passlib.context import CryptContext
import asyncpg

INDUSTRIES = [
    "SaaS", "Fintech", "Edtech", "Healthtech", "Martech",
    "HRtech", "Logtech", "Proptech", "Legaltech", "Cybersecurity"
]

CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург",
          "Казань", "Нижний Новгород", "Самара", "Уфа"]

TECH_STACKS = [
    {"python": True, "react": True, "postgresql": True},
    {"python": True, "vue": True, "postgresql": True, "redis": True},
    {"golang": True, "react": True, "mongodb": True},
    {"java": True, "angular": True, "mysql": True},
    {"python": True, "django": True, "postgresql": True, "celery": True},
    {"nodejs": True, "react": True, "mongodb": True, "redis": True},
]

INTEGRATIONS = [
    ["Slack", "Salesforce"], ["Bitrix24", "amoCRM"],
    ["Slack", "HubSpot", "Zapier"], ["1C", "МойСклад"],
    ["Telegram", "WhatsApp Business"], ["Jira", "Confluence"],
]

FUNDING_STAGES = [
    "pre_seed", "seed", "series_a", "bootstrapped", "unknown"
]

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_companies(conn: asyncpg.Connection, count: int):
    print(f"  → Создание {count} компаний...")
    for i in range(count):
        industry = random.choice(INDUSTRIES)
        city = random.choice(CITIES)
        name = f"SaaS Company {i+1:03d}"
        slug = f"saas-company-{i+1:03d}"

        await conn.execute("""
            INSERT INTO companies (
                id, name, slug, description, industry, sub_industries,
                headquarters_country, headquarters_city,
                employees_range, funding_stage, tech_stack,
                integrations, api_available, is_verified,
                founded_year, created_at, updated_at
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,NOW(),NOW())
            ON CONFLICT (slug) DO NOTHING
        """,
            uuid4(),
            name,
            slug,
            f"Российская SaaS-компания в сфере {industry}. "
            f"Помогаем бизнесу автоматизировать процессы.",
            industry,
            random.sample(INDUSTRIES, k=random.randint(1, 3)),
            "RU",
            city,
            random.choice(["1-10", "11-50", "51-200"]),
            random.choice(FUNDING_STAGES),
            random.choice(TECH_STACKS),       # JSONB
            random.choice(INTEGRATIONS),       # TEXT[]
            random.random() > 0.5,             # api_available
            random.random() > 0.7,             # is_verified
            random.randint(2015, 2024),        # founded_year
        )
    print(f"  ✅ {count} компаний создано")


async def seed_users(conn: asyncpg.Connection, count: int = 50):
    print(f"  → Создание {count} пользователей...")
    for i in range(count):
        role = "paid_user" if i < 40 else "company_admin"
        await conn.execute("""
            INSERT INTO users (
                id, email, password_hash, full_name, company_name,
                role, is_active, is_verified, created_at, updated_at
            ) VALUES ($1,$2,$3,$4,$5,$6,TRUE,TRUE,NOW(),NOW())
            ON CONFLICT (email) DO NOTHING
        """,
            uuid4(),
            f"user{i+1:03d}@algorithmic-arts-test.ru",
            pwd_ctx.hash("TestPassword123"),
            f"Тестовый Пользователь {i+1}",
            f"ООО Тест Компания {i+1}",
            role,
        )
    # Отдельно создаём admin
    await conn.execute("""
        INSERT INTO users (id, email, password_hash, full_name, role,
                           is_active, is_verified, created_at, updated_at)
        VALUES ($1,$2,$3,'Platform Admin','platform_admin',TRUE,TRUE,NOW(),NOW())
        ON CONFLICT (email) DO NOTHING
    """,
        uuid4(),
        "admin@algorithmic-arts.ru",
        pwd_ctx.hash("AdminPassword123!"),
    )
    print(f"  ✅ {count+1} пользователей создано (включая admin)")


async def seed_partnerships(conn: asyncpg.Connection, count: int = 200):
    print(f"  → Создание {count} партнёрств...")
    companies = await conn.fetch("SELECT id FROM companies LIMIT 100")
    company_ids = [r['id'] for r in companies]

    created = 0
    attempts = 0
    while created < count and attempts < count * 3:
        a, b = random.sample(company_ids, 2)
        if a > b:
            a, b = b, a
        score = round(random.uniform(0.5, 0.98), 4)
        try:
            await conn.execute("""
                INSERT INTO partnerships (
                    id, company_a_id, company_b_id, compatibility_score,
                    status, analysis_method, created_at, updated_at
                ) VALUES ($1,$2,$3,$4,$5,'auto_vector_scoring',NOW(),NOW())
                ON CONFLICT DO NOTHING
            """, uuid4(), a, b, score,
                random.choice(["suggested", "reviewed", "contacted"]))
            created += 1
        except Exception:
            pass
        attempts += 1
    print(f"  ✅ {created} партнёрств создано")


async def main(count: int):
    conn = await asyncpg.connect(
        host="localhost", port=5432,
        user="algo_user", password="REPLACE_ME",
        database="algorithmic_arts"
    )
    print("🌱 Загрузка seed-данных...")
    await seed_users(conn)
    await seed_companies(conn, count)
    await seed_partnerships(conn, count * 2)
    await conn.close()
    print("✅ Seed-данные загружены успешно!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args()
    asyncio.run(main(args.count))


ОБЩИЕ ТРЕБОВАНИЯ:
- Все таблицы: created_at, updated_at (с триггером), soft delete через deleted_at
- Каждый FK сопровождён индексом
- Enum-типы создаются через DO $$ ... EXCEPTION WHEN duplicate_object THEN NULL $$
- Alembic env.py: async подключение через asyncpg, автоматическое обнаружение моделей
- Миграции идемпотентны (повторный запуск не ломает БД)
- SQLAlchemy модели: строго Mapped[...] синтаксис, без Column() старого стиля
- Seed-скрипт: принимает --count, работает idempotently (ON CONFLICT DO NOTHING)

Создай все файлы: SQL схемы, Alembic-миграции для каждого сервиса,
SQLAlchemy модели, ClickHouse DDL и seed_data.py.
```

---

## Чеклист улучшений относительно исходных промптов

### Промпт №1 — что добавлено:
- Полная файловая структура с перечнем каждого файла и комментариями
- Таблица всех сервисов с портами и технологиями
- Двухсерверный Dockerfile (development + production) с healthcheck и непривилегированным пользователем
- Dockerfile для Next.js 15 (3 стадии: deps → builder → production с standalone output)
- Полный `.env.example` (35+ переменных, 12 секций: DB, Redis, Kafka, MinIO, ClickHouse, JWT, YandexGPT, GigaChat, OpenRouter, CRM, Email, Payments)
- Расширенный Makefile (25+ команд: start-infra, restart-svc, logs-svc, migrate-svc, rollback, migration-new, test-coverage, test-load, lint, format, seed, create-admin)
- `scripts/generate_secrets.py` с RSA key pair + случайные пароли
- `scripts/check_dependencies.sh` с проверкой версий
- `infra/postgres/init.sql` с расширениями и функцией `set_updated_at()`
- `infra/kafka/topics.sh` с созданием всех 18 топиков
- `docker-compose.override.yml` (dev volume mounts, hot reload)

### Промпт №2 — что добавлено:
- Полный SQL DDL для 14 таблиц (все поля, типы, constraints)
- 10 Enum-типов PostgreSQL с корректной идемпотентной инициализацией
- 35+ индексов: B-tree, GIN (JSONB/массивы), IVFFlat (pgvector), partial (WHERE conditions)
- Партиционирование company_updates по кварталам (2025-2026), company_metrics по годам
- pg_cron: автоочистка просроченных токенов и refresh tokens
- Constraint для уникальности пар компаний в партнёрствах (`CHECK (company_a_id < company_b_id)`)
- Полная Alembic-миграция с реальным Python-кодом (upgrade/downgrade)
- SQLAlchemy 2.0 модели для Company и User (Mapped[] синтаксис, все типы)
- ClickHouse DDL: 3 таблицы (user_events, search_queries, partnership_funnel) + Kafka Engine
- Полный seed_data.py: компании (100+), пользователи (50+), партнёрства (200+), с ON CONFLICT DO NOTHING
