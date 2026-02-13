# Data Pipeline Service Documentation

## Overview
Data Pipeline Service — система автоматического сбора, трансформации и загрузки данных о российских компаниях из 6 источников. Использует Celery Beat для регулярного скрапинга и Kafka для event-driven архитектуры.

## Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA PIPELINE SERVICE                        │
│  ┌─────────────┐   ┌───────────────────┐   ┌─────────────────┐ │
│  │ Scrapers    │→→│ Transform Pipeline│→→│ Load System     │ │
│  │ • VC.ru     │   │ • NER             │   │ • Kafka         │ │
│  │ • Rusbase   │   │ • Funding Parser  │   │ • PostgreSQL    │ │
│  │ • Habr      │   │ • Tech Extractor  │   │ • Elasticsearch │ │
│  │ • EGRUL     │   │ • Industry Class. │   │                 │ │
│  │ • Crunchbase│   │ • Deduplication  │   │                 │ │
│  └─────────────┘   └───────────────────┘   └─────────────────┘ │
│        ↑                        ↑                      ↑         │
│        │                        │                      │         │
│  ┌─────────────┐   ┌───────────────────┐   ┌─────────────────┐ │
│  │ Anti-bot    │   │ Rule-based Logic  │   │ Batch Processing│ │
│  │ • Proxy pool│   │ • Regex patterns  │   │ • Upsert logic  │ │
│  │ • Rate limit│   │ • ML classification│   │ • Retry backoff │ │
│  └─────────────┘   └───────────────────┘   └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### Scrapers (6 sources)
| Source | Frequency | Anti-bot | Retry | Data Fields |
|--------|-----------|----------|-------|-------------|
| **VC.ru** | 15min | Proxy rotation, random delays | Exponential backoff | Name, description, funding, team, tech stack |
| **Rusbase** | 30min | User-agent rotation | Linear backoff | Company info, investors, news |
| **Habr Career** | 1h | Cookie rotation | Exponential backoff | Job postings, tech stack, company size |
| **EGRUL** | Daily | CAPTCHA solver | Fixed retry | Legal info, registration date, directors |
| **Crunchbase** | Weekly | API keys rotation | Exponential backoff | Funding rounds, investors, competitors |
| **Base Scraper** | On-demand | Custom headers | Configurable | Generic HTML parsing |

### Transform Pipeline
- **NER**: spaCy with Russian model for entity extraction
- **Funding Parser**: regex + rule-based parsing of funding amounts
- **Tech Extractor**: keyword matching + LLM validation
- **Industry Classifier**: rule-based with fallback to LLM
- **Deduplication**: rapidfuzz + semantic similarity (sentence-transformers)
- **Normalizer**: standardization of company names, addresses, dates

### Load System
- **Kafka Producer**: `company.raw_data` topic with Avro schema
- **PostgreSQL Loader**: batch upsert with conflict resolution
- **Elasticsearch Indexer**: bulk indexing with dynamic mapping
- **Error Handling**: dead-letter queue for failed records

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scrape/vc-ru` | POST | Trigger VC.ru scraping immediately |
| `/scrape/rusbase` | POST | Trigger Rusbase scraping immediately |
| `/status` | GET | Health check and scraper status |
| `/metrics` | GET | Prometheus metrics |
| `/schedule` | GET | Current Celery Beat schedule |

## Deployment
```bash
# Build and run
docker compose up -d data-pipeline

# Check health
curl http://localhost:8006/status

# Monitor metrics
curl http://localhost:8006/metrics
```

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `KAFKA_BOOTSTRAP_SERVERS` | Yes | Kafka bootstrap servers |
| `POSTGRES_DSN` | Yes | PostgreSQL connection string |
| `ELASTICSEARCH_URL` | Yes | Elasticsearch URL |
| `REDIS_URL` | Yes | Redis connection string |
| `VC_RU_API_KEY` | No | VC.ru API key (if available) |
| `CRUNCHBASE_API_KEY` | No | Crunchbase API key |
| `PROXY_POOL_URL` | No | Proxy rotation service URL |

## Monitoring
Prometheus metrics available at `/metrics`:
- `scraper_requests_total{source, status}`
- `scraper_latency_seconds{source}`
- `transform_records_total{step, status}`
- `load_records_total{destination, status}`
- `kafka_messages_total{topic, status}`
- `celery_tasks_total{task_name, status}`