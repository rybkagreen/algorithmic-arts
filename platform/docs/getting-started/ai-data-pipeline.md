# Getting Started with AI Core and Data Pipeline

## Prerequisites
- Docker 24.0+
- Docker Compose 2.24+
- Python 3.12+
- Node.js 22+

## Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/rybkagreen/algorithmic-arts.git
cd algorithmic-arts/platform

# Copy environment template
cp .env.example .env

# Generate secrets
python scripts/generate_secrets.py >> .env
```

### 2. Start Infrastructure
```bash
# Start all services (including Kafka, PostgreSQL, Redis, Elasticsearch)
docker compose up -d

# Wait for services to be ready (check logs)
docker compose logs -f api-gateway
```

### 3. Apply Database Migrations
```bash
# Company service
docker compose exec company-service alembic upgrade head

# AI Core Service
docker compose exec ai-core-service alembic upgrade head

# Data Pipeline Service
docker compose exec data-pipeline alembic upgrade head
```

### 4. Create Admin User
```bash
docker compose exec api-gateway python scripts/create_admin.py
```

### 5. Load Test Data
```bash
# Load 100 test companies
docker compose exec data-pipeline python scripts/seed_data.py --count=100

# Trigger initial scraping
curl -X POST http://localhost:8006/scrape/vc-ru
curl -X POST http://localhost:8006/scrape/rusbase
```

## Service Management

### Start/Stop Individual Services
```bash
# Start only AI Core and Data Pipeline
docker compose up -d ai-core-service data-pipeline

# Stop specific services
docker compose stop ai-core-service data-pipeline
```

### Check Service Status
```bash
# Health checks
curl http://localhost:8005/health  # AI Core
curl http://localhost:8006/status  # Data Pipeline

# Metrics
curl http://localhost:8005/metrics  # AI Core metrics
curl http://localhost:8006/metrics  # Data Pipeline metrics

# Kafka topics
./scripts/topics.sh list
```

### Debugging Tips

#### Common Issues and Solutions
| Issue | Solution |
|-------|----------|
| `Connection refused` to Kafka | Wait for Kafka to initialize (check `docker compose logs kafka`) |
| Scraper fails with 429 | Configure proxy pool or reduce frequency in `config.py` |
| LLM requests timeout | Check Yandex/GigaChat API keys and network connectivity |
| PostgreSQL connection errors | Verify `POSTGRES_DSN` in `.env` file |
| Celery tasks not executing | Check `celery_app.py` configuration and Redis connection |

#### Logs Access
```bash
# AI Core logs
docker compose logs -f ai-core-service

# Data Pipeline logs
docker compose logs -f data-pipeline

# Kafka consumer logs (AI Core)
docker compose logs -f ai-core-service | grep "kafka.consumer"

# Scraper debug logs
docker compose logs -f data-pipeline | grep "scraper"
```

## Development Workflow

### Local Development
```bash
# Run AI Core in development mode
cd services/ai-core-service
poetry install
uvicorn src.main:app --reload --host 0.0.0.0 --port 8005

# Run Data Pipeline in development mode
cd services/data-pipeline
poetry install
uvicorn src.main:app --reload --host 0.0.0.0 --port 8006
```

### Testing
```bash
# Run AI Core tests
docker compose exec ai-core-service poetry run pytest tests/

# Run Data Pipeline tests
docker compose exec data-pipeline poetry run pytest tests/

# Load testing
cd tests/load
k6 run api_load_test.js
```

## Production Deployment

### Kubernetes Deployment
```yaml
# Example deployment for AI Core
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-core-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-core-service
  template:
    metadata:
      labels:
        app: ai-core-service
    spec:
      containers:
      - name: ai-core
        image: algorithmic-arts/ai-core:latest
        ports:
        - containerPort: 8005
        envFrom:
        - configMapRef:
            name: ai-core-config
        - secretRef:
            name: ai-core-secrets
```

### Monitoring Setup
1. **Prometheus**: scrape endpoints at `:8005/metrics` and `:8006/metrics`
2. **Grafana**: import dashboard templates from `infra/grafana/dashboards/`
3. **Alertmanager**: configure Slack notifications for critical alerts

## Next Steps
1. [ ] Configure LLM API keys in `.env`
2. [ ] Set up proxy pool for scrapers (optional but recommended)
3. [ ] Run initial data seeding
4. [ ] Monitor metrics and adjust scaling
5. [ ] Integrate with CRM systems (amoCRM, Bitrix24)

For detailed architecture, see [AI Core Documentation](../ai-core/README.md) and [Data Pipeline Documentation](../data-pipeline/README.md).