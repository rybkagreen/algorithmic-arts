# Makefile for ALGORITHMIC ARTS platform

.PHONY: help setup start stop logs test migrate shell-api shell-db clean dev

help:
	@echo "Available commands:"
	@echo "  help         - Show this help"
	@echo "  setup        - Setup development environment"
	@echo "  start        - Start all services"
	@echo "  stop         - Stop all services"
	@echo "  logs         - View service logs"
	@echo "  test         - Run all tests"
	@echo "  migrate      - Apply database migrations"
	@echo "  shell-api    - Open shell in API service"
	@echo "  shell-db     - Open PostgreSQL shell"
	@echo "  generate-secrets - Generate secrets"
	@echo "  seed-data    - Load test data"
	@echo "  dev          - Launch interactive Dev Hub menu"

setup:
	@echo "Setting up development environment..."
	docker compose up -d postgres redis kafka elasticsearch minio clickhouse
	python scripts/generate_secrets.py >> .env
	@echo "Environment setup complete. Please run 'make migrate' to apply migrations."

start:
	@echo "Starting all services..."
	docker compose up -d

stop:
	@echo "Stopping all services..."
	docker compose down

logs:
	@echo "Viewing logs for all services..."
	docker compose logs -f

test:
	@echo "Running tests..."
	@echo "Running company-service tests..."
	docker compose exec company-service poetry run pytest tests/ -v
	@echo "Running auth-service tests..."
	docker compose exec auth-service poetry run pytest tests/ -v
	@echo "Running user-service tests..."
	docker compose exec user-service poetry run pytest tests/ -v
	@echo "Running partner-service tests..."
	docker compose exec partner-service poetry run pytest tests/ -v
	@echo "Tests completed."

migrate:
	@echo "Applying database migrations..."
	docker compose exec auth-service alembic upgrade head
	docker compose exec user-service alembic upgrade head
	docker compose exec company-service alembic upgrade head
	docker compose exec partner-service alembic upgrade head
	@echo "Migrations applied successfully."

shell-api:
	@echo "Opening shell in API gateway..."
	docker compose exec api-gateway bash

shell-db:
	@echo "Opening PostgreSQL shell..."
	docker compose exec postgres psql -U algorithmic_arts -d algorithmic_arts

generate-secrets:
	@echo "Generating secrets..."
	python scripts/generate_secrets.py > .env.secrets
	@echo "Secrets generated in .env.secrets"

seed-data:
	@echo "Loading test data..."
	docker compose exec data-pipeline python scripts/seed_data.py --count=100
	@echo "Test data loaded."

clean:
	@echo "Cleaning up..."
	docker compose down -v
	rm -f .env.secrets
	@echo "Cleanup complete."

dev:
	@echo "Launching ALGORITHMIC ARTS DEV HUB (v2.1)..."
	platform/.dev-venv/bin/python platform/scripts/dev-menu.py