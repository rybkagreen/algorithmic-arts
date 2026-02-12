# ALGORITHMIC ARTS Platform - Developer Context Guide

**Version:** 3.0  
**Last Updated:** February 2026  
**Status:** Production Ready (Beta)  
**Target Market:** Russian B2B SaaS ecosystem  

## 🎯 Project Overview

ALGORITHMIC ARTS is an AI-powered Partnership Intelligence Platform designed specifically for the Russian B2B SaaS market. The platform uses a multi-agent architecture to continuously monitor the ecosystem and automatically identify strategic partnership opportunities in real-time.

### Core Value Proposition
- **For Russian SaaS companies**: Automated discovery of partnership opportunities within the fragmented Russian ecosystem
- **AI-driven insights**: Multi-agent system analyzing compatibility, market fit, and strategic value
- **Regulatory compliance**: Full adherence to Russian data protection laws (152-FZ) with data hosted in Russia
- **Local integration**: Native support for Russian CRM systems (amoCRM, Bitrix24, Megaplan)

### Key Metrics
- **20,000+** Russian companies in database (as of Feb 2026)
- **80,000+** international products for global strategies
- **72%** of BD teams miss partnership opportunities (Skolkovo research, 2025)
- **< 2 seconds** average API response time (Yandex Cloud infrastructure)

## 🏗️ Architecture & Technology Stack

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND LAYER (Next.js 15)                  │
│  • Server Components • React 19 • Streaming SSR • Edge Runtime  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/3 (QUIC)
┌─────────────────────────────────────────────────────────────────┐
│                  API GATEWAY (FastAPI + Caddy)                   │
│  • Rate Limiting • Circuit Breaker • Load Balancing • Auth      │
└─────────────────────────────────────────────────────────────────┘
                              ↓ gRPC / Event Bus
┌─────────────────────────────────────────────────────────────────┐
│                      MICROSERVICES LAYER                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Auth   │  │   User   │  │ Company  │  │ Partner  │       │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ AI Core  │  │   Data   │  │   CRM    │  │  Search  │       │
│  │   +AI    │  │ Pipeline │  │   Hub    │  │ Service  │       │
│  │  Agents  │  │          │  │          │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EVENT BUS (Apache Kafka)                      │
│  • Event Sourcing • CQRS • Saga Pattern • Stream Processing    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│  • PostgreSQL 17 + pgvector + Citus (sharding)                 │
│  • Redis 7.4 Stack (cache + streams + search)                  │
│  • Elasticsearch 8.14 (full-text + vector search)              │
│  • ClickHouse (analytics + time-series)                        │
│  • MinIO (S3-compatible object storage)                        │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack Details

| Category | Technologies | Version |
|----------|-------------|---------|
| **Backend** | Python, FastAPI, Uvicorn | 3.12+, 0.115+, 0.31+ |
| **Database** | PostgreSQL, pgvector, Citus, Redis Stack | 17, 0.7+, 12+, 7.4 |
| **Search** | Elasticsearch | 8.14 |
| **Analytics** | ClickHouse | 24.1 |
| **Message Queue** | Apache Kafka, Zookeeper | 3.7, 3.7 |
| **Storage** | MinIO | Latest |
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS | 15, 19, 5.4+, 3.4+ |
| **AI/ML** | YandexGPT 4, GigaChat Pro, Claude 4.5, LangChain, Sentence Transformers | Latest |
| **DevOps** | Docker, Kubernetes, Terraform, GitHub Actions | 24.0+, 1.28+, 1.9+, 2.12+ |

## 📁 Project Structure

```
/home/alex/MyApps/SaasPlatform/
├── ARCHITECTURE.md           # Detailed system architecture
├── README.md                 # Main documentation
├── PROMPTS_FOR_QWEN.md       # AI generation prompts
├── GETTING_STARTED.md        # Developer setup guide
├── docker-compose.yml        # Local development infrastructure
├── Makefile                  # Common development commands
├── generate_secrets.py       # Secret generation script
├── .env.example              # Environment variables template
├── algorithmic-arts/         # Main codebase directory
│   ├── .github/              # CI/CD workflows
│   ├── docs/                 # Documentation
│   │   └── concept_ru_market.md  # Russian market concept
│   ├── infra/                # Infrastructure as Code
│   ├── libs/                 # Shared libraries
│   ├── migrations/           # Database migrations
│   ├── scripts/              # Automation scripts
│   ├── services/             # Microservices (12 core services)
│   │   ├── api-gateway/
│   │   ├── auth-service/
│   │   ├── user-service/
│   │   ├── company-service/
│   │   ├── partner-service/
│   │   ├── ai-core-service/
│   │   ├── data-pipeline/
│   │   ├── crm-hub/
│   │   ├── search-service/
│   │   ├── reporting/
│   │   ├── billing/
│   │   └── notification/
│   ├── frontend/             # Next.js 15 application
│   ├── ai-agents/            # AI agent implementations
│   ├── shared/               # Shared code (proto, events, utils)
│   └── tests/                # Test suites
└── QWEN.md                   # This file (developer context)
```

## 🛠️ Development Environment Setup

### Prerequisites
```bash
# Required versions
docker --version        # Docker 24.0+
docker compose version  # Docker Compose 2.24+
python --version        # Python 3.12+
node --version          # Node.js 22+
git --version           # Git 2.40+
```

### Quick Start (5 minutes)
```bash
# 1. Clone repository
git clone https://github.com/algorithmic-arts/platform.git
cd platform

# 2. Setup environment
cp .env.example .env
python scripts/generate_secrets.py >> .env

# 3. Start infrastructure
docker compose up -d

# 4. Apply migrations
docker compose exec api-gateway alembic upgrade head
docker compose exec company-service alembic upgrade head
docker compose exec auth-service alembic upgrade head

# 5. Create admin user
docker compose exec api-gateway python scripts/create_admin.py

# 6. Load test data
docker compose exec data-pipeline python scripts/seed_data.py --count=100
```

### Common Make Commands
| Command | Description |
|---------|-------------|
| `make help` | Show available commands |
| `make setup` | Initial project setup |
| `make start` | Start all services |
| `make stop` | Stop all services |
| `make logs` | View service logs |
| `make test` | Run all tests |
| `make migrate` | Apply database migrations |
| `make shell-api` | Open shell in API service |
| `make shell-db` | Open PostgreSQL shell |

## 🧩 Microservice Architecture

### Core Services
| Service | Port | Responsibility | Tech Stack |
|---------|------|----------------|------------|
| **api-gateway** | 80 | API routing, auth, rate limiting | FastAPI, Caddy |
| **auth-service** | 8001 | Authentication, JWT, OAuth2 | FastAPI, PostgreSQL |
| **user-service** | 8002 | User profiles, RBAC/ABAC | FastAPI, PostgreSQL |
| **company-service** | 8003 | Company CRUD, vector search | FastAPI, PostgreSQL, Elasticsearch |
| **partner-service** | 8004 | Partnership matching, analysis | FastAPI, PostgreSQL |
| **ai-core-service** | 8005 | AI agents, LLM orchestration | FastAPI, LangChain |
| **data-pipeline** | 8006 | ETL, scraping, data enrichment | Scrapy, Celery |
| **crm-hub** | 8007 | CRM integrations (amoCRM, Bitrix24) | FastAPI, HTTPX |
| **search-service** | 8008 | Hybrid search (full-text + vector) | FastAPI, Elasticsearch |
| **reporting-service** | 8009 | Report generation, analytics | FastAPI, ClickHouse |
| **billing-service** | 8010 | Subscriptions, payments | FastAPI, PostgreSQL |
| **notification-service** | 8011 | Email, Telegram, push notifications | FastAPI, Redis |

### Communication Patterns
- **Synchronous**: gRPC between services, REST for external clients
- **Asynchronous**: Kafka event bus for domain events
- **CQRS**: Separate command and query models
- **Event Sourcing**: All changes captured as events

## 🤖 AI Agent System

The platform features a multi-agent architecture orchestrated by LangGraph:

### Core AI Agents
1. **Partnership Scout Agent**
   - Monitors VC.ru, Habr, LinkedIn for new companies and changes
   - Triggers every 15 minutes
   - Uses YandexGPT 4 for Russian language processing

2. **Compatibility Analyzer Agent**
   - Analyzes product compatibility using vector search + LLM evaluation
   - Calculates compatibility score (0-1) with weighted factors:
     - Tech stack overlap (25%)
     - Market overlap (20%)
     - Company size match (15%)
     - Geographic proximity (10%)
     - No direct competition (15%)
     - Feature complementarity (15%)

3. **Outreach Writer Agent**
   - Generates personalized outreach emails
   - Supports formal, friendly, and technical styles
   - Available in Russian and English

4. **CRM Sync Agent**
   - Bidirectional synchronization with CRM systems
   - Handles conflicts with configurable resolution strategies
   - Supports amoCRM, Bitrix24, Salesforce

5. **Analytics Agent**
   - Predictive analytics for deal probability
   - Uses gradient boosting + neural networks
   - Updates daily with new data

### LLM Router with Fallback
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
                await log_llm_usage(provider.name, success=True)
                return response
            except Exception as e:
                await log_llm_usage(provider.name, success=False, error=str(e))
                continue
        raise AllProvidersFailedError()
```

## 🔐 Security & Compliance

### Zero Trust Architecture
- **Data residency**: 100% data hosted in Russia (Yandex Cloud)
- **Encryption**: TLS 1.3 for all connections, AES-256-GCM for data at rest
- **Authentication**: JWT with RS256 signature, 2FA optional for admins
- **Authorization**: RBAC + ABAC with fine-grained permissions
- **Compliance**: Full adherence to Federal Law 152-FZ (Personal Data)

### Security Measures
- **Infrastructure**: WAF (Yandex Shield), DDoS protection
- **Application**: Input validation, output sanitization, CSRF protection
- **Database**: Column-level encryption for sensitive fields
- **Monitoring**: 24/7 SOC, SIEM, automated anomaly detection

## 📊 Performance & Monitoring

### SLIs/SLOs
| Service | Availability | Error Rate | Latency (p95) |
|---------|--------------|------------|---------------|
| API Gateway | 99.9% | < 0.1% | < 500ms |
| Auth Service | 99.95% | < 0.05% | < 200ms |
| Company Service | 99.9% | < 0.1% | < 500ms |
| AI Core | 99.5% | < 0.5% | < 30s |
| Search | 99.9% | < 0.1% | < 300ms |

### Observability Stack
- **Metrics**: Prometheus + Grafana
- **Logs**: Loki aggregation
- **Tracing**: Jaeger distributed tracing
- **Alerting**: Slack/Telegram notifications for critical issues

## 🚀 Business Model

### Pricing Tiers (RUB, excluding VAT)
| Plan | Price/Month | Users | Companies | AI Requests/Month | Features |
|------|-------------|-------|-----------|-------------------|----------|
| **Starter** | ₽9,990 | 2 | 150 | 1,000 | Basic search, 1 CRM |
| **Growth** | ₽29,990 | 5 | 1,000 | 5,000 | AI analysis, 3 CRM, API |
| **Scale** | ₽79,990 | 15 | ∞ | 25,000 | All features, White-label |
| **Enterprise** | From ₽200,000 | ∞ | ∞ | ∞ | On-premise, SLA 99.95% |

### Additional Revenue Streams
- **Pay-as-you-go AI Credits**: ₽100 per 1,000 requests over limit
- **Data Reports**: ₽75,000 per industry report
- **Partnership Marketplace**: 12% commission on first-year contracts
- **Consulting**: ₽40,000/hour for strategic sessions
- **White-label**: ₽500,000 one-time + ₽50,000/month

## 📈 Financial Projections (2026)
| Metric | 6 months | 12 months | 18 months | 24 months |
|--------|----------|-----------|-----------|-----------|
| **ARR** | ₽4M | ₽12M | ₽50M | ₽150M |
| **MRR** | ₽350K | ₽1M | ₽4.2M | ₽12.5M |
| **Customers** | 40 | 120 | 350 | 800 |
| **ARPU** | ₽100K/year | ₽100K/year | ₽143K/year | ₽188K/year |
| **CAC** | ₽90K | ₽75K | ₽60K | ₽50K |
| **LTV** | ₽450K | ₽500K | ₽650K | ₽800K |
| **LTV/CAC** | 5.0x | 6.7x | 10.8x | 16.0x |
| **Burn Rate** | -₽3M/month | -₽2M/month | -₽1M/month | +₽2M/month |

## 📚 Key Documentation References

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Comprehensive system architecture details
2. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Developer setup and workflow guide
3. **[PROMPTS_FOR_QWEN.md](PROMPTS_FOR_QWEN.md)** - AI generation prompts for code creation
4. **[COMPLIANCE_152FZ.md](COMPLIANCE_152FZ.md)** - Russian regulatory compliance details
5. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment procedures
6. **[TESTING.md](TESTING.md)** - Testing strategy and coverage requirements

## 🔄 Development Workflow

### Branching Strategy
- **main**: Production-ready code
- **develop**: Integration branch for upcoming release
- **feature/**: Feature branches (e.g., `feature/add-company-tags`)
- **hotfix/**: Critical bug fixes for production

### Commit Conventions
Follow Conventional Commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `test:` - Tests
- `chore:` - Maintenance tasks

### Code Review Process
1. Create Pull Request
2. Automated checks run (linters, tests, security scan)
3. 2+ developers review code
4. Merge after approval

## 🧪 Testing Strategy

### Test Pyramid
- **Unit tests**: 90%+ coverage (pytest, Vitest)
- **Integration tests**: Service-to-service communication
- **E2E tests**: Playwright for frontend flows
- **Load tests**: k6 for performance testing

### Test Execution
```bash
# Run all tests
make test

# Unit tests only
docker compose exec company-service poetry run pytest tests/unit/ -v

# Integration tests
docker compose exec company-service poetry run pytest tests/integration/ -v

# Coverage report
docker compose exec company-service poetry run pytest --cov=src --cov-report=html
```

## 📝 Important Notes

1. **Russian Market Focus**: All features are designed with Russian regulatory requirements and market specifics in mind
2. **Data Sovereignty**: All data processing occurs in Russia to comply with 152-FZ
3. **Multi-language Support**: Primary interface in Russian, with English support for international features
4. **AI Localization**: Russian LLMs (YandexGPT, GigaChat) prioritized over international alternatives
5. **CRM Integration Priority**: amoCRM and Bitrix24 have highest integration priority

This document serves as the authoritative reference for developers working on the ALGORITHMIC ARTS platform. Always refer to the latest documentation files for detailed implementation specifics.