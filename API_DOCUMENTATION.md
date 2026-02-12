# API Documentation

**Version:** 3.0  
**Base URL:** `http://localhost/api/v1`  
**Authentication:** JWT Bearer Token

## Quick Start

```bash
# Get access token
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost/api/v1/companies
```

## Core Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - Logout

### Companies
- `GET /companies` - List companies (filters: industry, size, location)
- `GET /companies/{id}` - Get company details
- `POST /companies` - Create company
- `PUT /companies/{id}` - Update company
- `DELETE /companies/{id}` - Delete company
- `GET /companies/{id}/similar` - Find similar companies (vector search)

### Partnerships
- `GET /partnerships` - List partnerships
- `POST /partnerships/analyze` - Analyze compatibility (score 0-1)
- `POST /partnerships/{id}/contact` - Send outreach email
- `GET /partnerships/recommendations` - Get AI recommendations

### AI Services
- `POST /ai/enrich/company` - AI enrichment of company data
- `POST /ai/analyze/compatibility` - Deep compatibility analysis
- `POST /ai/generate/pitch` - Generate outreach email
- `POST /ai/chat` - Chat with AI assistant

### Search
- `GET /search/companies` - Hybrid search (full-text + semantic)
- `GET /search/partnerships` - Search partnerships

## Response Format

```json
{
  "data": {...},
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

**Full API Reference:** See `/docs` (Swagger UI) when server is running.
