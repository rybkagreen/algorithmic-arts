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