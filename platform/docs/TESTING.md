# Testing Guide

**Framework:** pytest (Python), Vitest (TypeScript)  
**Coverage Target:** 90%+

## Run All Tests

```bash
# Backend
docker compose exec company-service poetry run pytest

# Frontend
cd frontend && npm test

# E2E
cd tests/e2e && npm run test
```

## Unit Tests

```bash
poetry run pytest tests/unit/ -v --cov=src
```

## Integration Tests

```bash
poetry run pytest tests/integration/ -v
```

## Load Tests

```bash
k6 run tests/load/api_load_test.js
```

## Coverage Report

```bash
poetry run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## CI Tests

All tests run automatically on PR via GitHub Actions.
