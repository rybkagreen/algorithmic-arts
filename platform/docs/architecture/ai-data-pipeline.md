# AI Core + Data Pipeline Architecture

## Event-Driven Integration Flow

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   Data Pipeline     │     │      Kafka Bus      │     │     AI Core         │
│  (Scraping & ETL)   │────▶│  company.raw_data   │────▶│  (Multi-Agent AI)   │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
        │                             │                             │
        ▼                             ▼                             ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ PostgreSQL (Raw)    │     │ company.created     │     │ PostgreSQL (AI)     │
│ • Raw scraped data  │◀────│                     │◀────│ • Enriched companies │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
        │                             │                             │
        ▼                             ▼                             ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ Elasticsearch       │     │ company.enriched    │     │ Redis (Cache)       │
│ • Full-text search  │◀────│                     │◀────│ • Agent state       │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

## Key Integration Points

### 1. `company.raw_data` → AI Core
- **Trigger**: Data Pipeline publishes raw company data to Kafka
- **Consumer**: AI Core Service consumes and triggers enrichment
- **Payload schema**:
```json
{
  "event_id": "uuid",
  "event_type": "company.raw_data",
  "timestamp": "ISO8601",
  "data": {
    "source": "vc_ru|rusbase|habr|egrul|crunchbase",
    "raw_html": "base64",
    "metadata": {
      "url": "string",
      "scraped_at": "ISO8601",
      "confidence": 0.95
    }
  }
}
```

### 2. `company.created` → AI Core
- **Trigger**: Company Service creates new company record
- **Consumer**: AI Core Service consumes and triggers partnership analysis
- **Payload schema**:
```json
{
  "event_id": "uuid",
  "event_type": "company.created",
  "timestamp": "ISO8601",
  "data": {
    "company_id": "uuid",
    "name": "string",
    "description": "string",
    "website": "string",
    "industry": "string",
    "size": "small|medium|large",
    "funding": "pre_seed|seed|series_a|..."
  }
}
```

### 3. `company.enriched` → Company Service
- **Trigger**: AI Core completes enrichment
- **Consumer**: Company Service updates company record
- **Payload schema**:
```json
{
  "event_id": "uuid",
  "event_type": "company.enriched",
  "timestamp": "ISO8601",
  "data": {
    "company_id": "uuid",
    "enrichment": {
      "tech_stack": ["Python", "PostgreSQL", "React"],
      "competitors": ["Company A", "Company B"],
      "market_position": "leader|niche|emerging",
      "compatibility_score": 0.87,
      "outreach_message": "text"
    },
    "updated_at": "ISO8601"
  }
}
```

## Performance Characteristics

| Component | Throughput | Latency | Reliability |
|-----------|------------|---------|-------------|
| **Scrapers** | 100 companies/min | 2-5s per company | 99.5% success rate |
| **Transform** | 200 records/sec | 100-300ms per record | 99.9% success rate |
| **Load System** | 500 records/sec | 50-200ms per batch | 99.99% success rate |
| **AI Analysis** | 50 companies/hour | 5-30s per analysis | 95% success rate |

## Error Handling Strategy

### Data Pipeline
- **Retry**: 3 attempts with exponential backoff
- **Dead-letter queue**: Failed records go to `company.raw_data.dlq`
- **Alerting**: Slack notifications for >5% failure rate

### AI Core
- **Circuit breaker**: 3 consecutive failures → 60s pause
- **Fallback**: If primary LLM fails, try next in priority
- **Human-in-the-loop**: Low-confidence results flagged for review

## Security Considerations

- **Data residency**: All processing in Russia (Yandex Cloud)
- **Encryption**: TLS 1.3 for all connections, AES-256 for data at rest
- **Rate limiting**: 100 requests/minute per API key
- **Input validation**: Sanitization of scraped HTML content
- **Compliance**: Full adherence to Federal Law 152-FZ

## Scaling Strategy

### Horizontal Scaling
- **Scrapers**: Add worker containers for specific sources
- **Transform**: Scale by CPU cores (CPU-intensive)
- **AI Analysis**: Scale by GPU instances for LLM inference

### Vertical Scaling
- **Database**: Citus sharding for PostgreSQL
- **Elasticsearch**: Dedicated master/data nodes
- **Redis**: Cluster mode for high availability

## Monitoring Dashboard
Grafana dashboard includes:
- Scraper success/failure rates
- AI analysis latency distribution
- Kafka consumer lag
- LLM provider usage and cost
- Company enrichment completeness