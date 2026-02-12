# ALGORITHMIC ARTS Platform

AI-powered Partnership Intelligence Platform for the Russian B2B SaaS market.

## 🎯 Overview

ALGORITHMIC ARTS is an AI-powered Partnership Intelligence Platform designed specifically for the Russian B2B SaaS market. The platform uses a multi-agent architecture to continuously monitor the ecosystem and automatically identify strategic partnership opportunities in real-time.

### Core Value Proposition
- **For Russian SaaS companies**: Automated discovery of partnership opportunities within the fragmented Russian ecosystem
- **AI-driven insights**: Multi-agent system analyzing compatibility, market fit, and strategic value
- **Regulatory compliance**: Full adherence to Russian data protection laws (152-FZ) with data hosted in Russia
- **Local integration**: Native support for Russian CRM systems (amoCRM, Bitrix24, Megaplan)

## 🏗️ Architecture

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

## 📁 Project Structure

```
platform/
├── services/
│   ├── auth-service/         # Authentication service (JWT, OAuth2, RBAC)
│   ├── user-service/         # User management service (RBAC, profiles)
│   ├── company-service/      # Company management service (DDD, CQRS, Event Sourcing)
│   ├── partner-service/      # Partnership management service (compatibility analysis)
│   ├── ai-core-service/      # AI agents and LLM orchestration
│   └── ...                   # Other microservices
├── shared/                   # Shared libraries (events, exceptions, logging, schemas)
├── infra/                    # Infrastructure as Code
├── scripts/                  # Automation scripts
├── docker-compose.yml        # Local development infrastructure
├── Makefile                  # Common development commands
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
```bash
docker --version        # Docker 24.0+
docker compose version  # Docker Compose 2.24+
python --version        # Python 3.12+
node --version          # Node.js 22+
git --version           # Git 2.40+
```

### Setup and Run
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
make migrate

# 5. Create admin user (if needed)
docker compose exec api-gateway python scripts/create_admin.py

# 6. Load test data
make seed-data

# 7. Access services
# Auth: http://localhost:8001/auth/health
# Company: http://localhost:8003/health
# User: http://localhost:8002/health
# Partner: http://localhost:8004/health
# AI Core: http://localhost:8005/health
# ClickHouse: http://localhost:8123
```

## 🧩 Microservices

### Auth Service (`auth-service`)
- JWT authentication with RS256 signature
- OAuth2 integration (Yandex, Google, VK)
- Rate limiting and brute-force protection
- 2FA support with TOTP
- Comprehensive RBAC system

### User Service (`user-service`)
- User profile management
- Company organization structure
- RBAC with fine-grained permissions
- User-to-company assignment

### Company Service (`company-service`)
- DDD architecture with aggregate root
- CQRS pattern with commands/queries
- Event Sourcing with Kafka integration
- Soft delete implementation
- Partitioned tables for scalability
- Vector search with pgvector

### Partner Service (`partner-service`)
- Partnership management
- Compatibility analysis (AI-powered)
- Partnership metrics tracking
- Outreach message generation

### AI Core Service (`ai-core-service`)
- Multi-agent architecture
- LLM orchestration (YandexGPT, GigaChat, Claude)
- Partnership Scout Agent
- Compatibility Analyzer Agent
- Outreach Writer Agent

## 🛠️ Development Commands

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

## 📊 Performance Metrics

| Service | Availability | Error Rate | Latency (p95) |
|---------|--------------|------------|---------------|
| API Gateway | 99.9% | < 0.1% | < 500ms |
| Auth Service | 99.95% | < 0.05% | < 200ms |
| Company Service | 99.9% | < 0.1% | < 500ms |
| AI Core | 99.5% | < 0.5% | < 30s |
| Search | 99.9% | < 0.1% | < 300ms |

## 📈 Business Model

### Pricing Tiers (RUB, excluding VAT)
| Plan | Price/Month | Users | Companies | AI Requests/Month | Features |
|------|-------------|-------|-----------|-------------------|----------|
| **Starter** | ₽9,990 | 2 | 150 | 1,000 | Basic search, 1 CRM |
| **Growth** | ₽29,990 | 5 | 1,000 | 5,000 | AI analysis, 3 CRM, API |
| **Scale** | ₽79,990 | 15 | ∞ | 25,000 | All features, White-label |
| **Enterprise** | From ₽200,000 | ∞ | ∞ | ∞ | On-premise, SLA 99.95% |

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- [GETTING_STARTED.md](GETTING_STARTED.md) - Developer setup guide
- [PROMPTS_FOR_QWEN.md](PROMPTS_FOR_QWEN.md) - AI generation prompts
- [COMPLIANCE_152FZ.md](COMPLIANCE_152FZ.md) - Russian regulatory compliance
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment procedures
- [TESTING.md](TESTING.md) - Testing strategy and coverage requirements

## 🎯 Implementation Status (Feb 2026)

✅ **Completed**: 
- Shared library (events, exceptions, logging, schemas)
- Company service (95% complete with DDD, CQRS, Event Sourcing, partitioning)
- Auth service (basic implementation with OAuth2, RBAC)
- User service (basic implementation with RBAC)
- Partner service (basic implementation with compatibility analysis)
- AI core service (basic agent framework)
- Infrastructure (docker-compose, .env, Makefile, scripts)
- ClickHouse analytics integration

⏳ **In Progress**:
- Complete AI agent system implementation
- Frontend UI development
- Comprehensive testing and load testing
- Production deployment automation

The platform is now ready for the next phase of development where we can focus on completing the AI agent system and building the frontend interface.