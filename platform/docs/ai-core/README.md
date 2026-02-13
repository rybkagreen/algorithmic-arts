# AI Core Service Documentation

## Overview
AI Core Service — мультиагентная система для автоматического анализа партнерских возможностей в российском B2B SaaS рынке. Использует LLM-роутер с fallback, RAG пайплайн и LangGraph для orchestration.

## Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         AI CORE SERVICE                          │
│  ┌─────────────┐   ┌───────────────────┐   ┌─────────────────┐ │
│  │ LLM Router  │←→│ Multi-Agent System │←→│ RAG Pipeline    │ │
│  └─────────────┘   └───────────────────┘   └─────────────────┘ │
│        ↑                        ↑                      ↑         │
│        │                        │                      │         │
│  ┌─────────────┐   ┌───────────────────┐   ┌─────────────────┐ │
│  │ Providers   │   │ Agent State       │   │ Embedding       │ │
│  │ • YandexGPT │   │ • trigger         │   │ • pgvector      │ │
│  │ • GigaChat  │   │ • company_ids     │   │ • BM25 + RRF    │ │
│  │ • OpenRouter│   │ • compatibility   │   │ • Cross-encoder │ │
│  └─────────────┘   └───────────────────┘   └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### LLM Router with Circuit Breaker
- **Priority order**: YandexGPT → GigaChat → OpenRouter
- **Circuit breaker**: 3 consecutive failures → 60s pause
- **Exponential backoff**: 1s → 2s → 4s between retries
- **Metrics**: `llm_calls_total`, `llm_latency_seconds`, `llm_cost_rub_total`

### Multi-Agent System (LangGraph)
| Agent | Responsibility | Input | Output |
|-------|----------------|-------|--------|
| **Scout** | Monitor VC.ru, Habr, Rusbase for new companies | `trigger: scheduled` | `scout_insights` |
| **Enricher** | Data enrichment via AI analysis | `company_id` | `enriched_company` |
| **Analyzer** | Compatibility scoring (0-1) | `company_a_id`, `company_b_id` | `compatibility_score`, `compatibility_report` |
| **Writer** | Generate outreach messages | `compatibility_report`, `outreach_style` | `outreach_message` |
| **Predictor** | Deal probability prediction | `compatibility_score`, `company_data` | `deal_probability` |

### RAG Pipeline
- **Hybrid search**: pgvector (dense) + BM25 (sparse) + RRF fusion
- **Reranking**: cross-encoder `ms-marco-MiniLM-L-6-v2`
- **Context window**: 6000 characters
- **Latency**: ~500ms per query (CPU-only)

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/generate` | POST | LLM text generation with provider selection |
| `/ai/analyze-partnership` | POST | Analyze compatibility between two companies |
| `/ai/enrich-company/{company_id}` | POST | Trigger company enrichment via Celery |
| `/ai/models/available` | GET | List available LLM providers and circuit status |
| `/ai/prompts/{key}/stats` | GET | A/B testing statistics for prompts |

## Deployment
```bash
# Build and run
docker compose up -d ai-core-service

# Check health
curl http://localhost:8005/health

# Monitor metrics
curl http://localhost:8005/metrics
```

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `YANDEX_API_KEY` | Yes | YandexGPT API key |
| `YANDEX_FOLDER_ID` | Yes | Yandex Cloud folder ID |
| `GIGACHAT_API_KEY` | Yes | GigaChat API key |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key |
| `REDIS_URL` | Yes | Redis connection string |
| `POSTGRES_DSN` | Yes | PostgreSQL connection string |
| `KAFKA_BOOTSTRAP_SERVERS` | Yes | Kafka bootstrap servers |

## Monitoring
Prometheus metrics available at `/metrics`:
- `llm_calls_total{provider, status}`
- `llm_latency_seconds{provider}`
- `agent_runs_total{agent_name, status}`
- `rag_queries_total{status}`
- `kafka_messages_total{topic, status}`