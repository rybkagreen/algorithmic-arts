-- Company Database Schema

-- Companies table
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    website VARCHAR(1024),
    logo_url VARCHAR(2048),
    industry VARCHAR(100),
    sub_industries TEXT[],
    business_model TEXT,
    founded_year INTEGER,
    headquarters_country VARCHAR(100),
    headquarters_city VARCHAR(100),
    employees_count INTEGER,
    employees_range VARCHAR(50),
    funding_total NUMERIC(15,2),
    funding_stage VARCHAR(50),
    last_funding_date DATE,
    inn VARCHAR(12),
    ogrn VARCHAR(13),
    kpp VARCHAR(9),
    legal_name VARCHAR(255),
    tech_stack JSONB,
    integrations TEXT[],
    api_available BOOLEAN DEFAULT FALSE,
    ai_summary TEXT,
    ai_tags TEXT[],
    embedding VECTOR(1536),
    is_verified BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Company updates table (partitioned by year)
CREATE TABLE company_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    update_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    source_url VARCHAR(2048),
    published_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (published_at);

-- Create partitions for company_updates (example for 2025-2026)
CREATE TABLE company_updates_2025 PARTITION OF company_updates
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE company_updates_2026 PARTITION OF company_updates
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Company metrics table (partitioned by month)
CREATE TABLE company_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC(15,2) NOT NULL,
    measured_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (measured_at);

-- Create partitions for company_metrics (example for 2026)
CREATE TABLE company_metrics_2026_01 PARTITION OF company_metrics
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE company_metrics_2026_02 PARTITION OF company_metrics
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Indexes
CREATE INDEX idx_companies_slug ON companies(slug);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_deleted_at ON companies(deleted_at) WHERE deleted_at IS NOT NULL;
CREATE INDEX idx_companies_embedding ON companies USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_companies_tech_stack ON companies USING GIN (tech_stack);
CREATE INDEX idx_companies_integrations ON companies USING GIN (integrations);
CREATE INDEX idx_companies_ai_tags ON companies USING GIN (ai_tags);
CREATE INDEX idx_company_updates_company_id ON company_updates(company_id);
CREATE INDEX idx_company_updates_published_at ON company_updates(published_at);
CREATE INDEX idx_company_metrics_company_id ON company_metrics(company_id);
CREATE INDEX idx_company_metrics_measured_at ON company_metrics(measured_at);
CREATE INDEX idx_company_metrics_metric_name ON company_metrics(metric_name);

-- Triggers
CREATE TRIGGER update_company_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_company_updated_at BEFORE UPDATE ON company_updates FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_company_updated_at BEFORE UPDATE ON company_metrics FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();