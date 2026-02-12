-- Data Pipeline Database Schema

-- Data sources table
CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'api', 'csv', 'json', 'database', 'web_scrape'
    url VARCHAR(2048),
    credentials JSONB, -- encrypted credentials
    config JSONB, -- source-specific configuration
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Data pipelines table
CREATE TABLE data_pipelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    source_id UUID NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    destination_type VARCHAR(50) NOT NULL, -- 'database', 's3', 'kafka', 'api'
    destination_config JSONB,
    schedule VARCHAR(100), -- cron expression or 'manual', 'realtime'
    status VARCHAR(20) NOT NULL DEFAULT 'inactive', -- 'inactive', 'active', 'paused', 'error'
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pipeline runs table
CREATE TABLE pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID NOT NULL REFERENCES data_pipelines(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL, -- 'queued', 'running', 'completed', 'failed', 'cancelled'
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT iglia,
    metadata JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data transformations table
CREATE TABLE data_transformations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID NOT NULL REFERENCES data_pipelines(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'mapping', 'filtering', 'aggregation', 'enrichment'
    config JSONB,
    order INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data validation rules table
CREATE TABLE data_validation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID NOT NULL REFERENCES data_pipelines(id) ON DELETE CASCADE,
    field_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- 'required', 'regex', 'range', 'enum', 'custom'
    rule_config JSONB,
    severity VARCHAR(20) NOT NULL DEFAULT 'warning', -- 'info', 'warning', 'error'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scraped data table (for web scraping)
CREATE TABLE scraped_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url VARCHAR(2048) NOT NULL,
    content_type VARCHAR(100),
    html_content TEXT,
    extracted_data JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_data_sources_type ON data_sources(type);
CREATE INDEX idx_data_sources_deleted_at ON data_sources(deleted_at) WHERE deleted_at IS NOT NULL;
CREATE INDEX idx_data_pipelines_source_id ON data_pipelines(source_id);
CREATE INDEX idx_data_pipelines_status ON data_pipelines(status);
CREATE INDEX idx_data_pipelines_next_run_at ON data_pipelines(next_run_at);
CREATE INDEX idx_pipeline_runs_pipeline_id ON pipeline_runs(pipeline_id);
CREATE INDEX idx_pipeline_runs_status ON pipeline_runs(status);
CREATE INDEX idx_pipeline_runs_start_time ON pipeline_runs(start_time DESC);
CREATE INDEX idx_data_transformations_pipeline_id ON data_transformations(pipeline_id);
CREATE INDEX idx_data_transformations_order ON data_transformations(order);
CREATE INDEX idx_data_validation_rules_pipeline_id ON data_validation_rules(pipeline_id);
CREATE INDEX idx_scraped_data_source_url ON scraped_data(source_url);
CREATE INDEX idx_scraped_data_created_at ON scraped_data(created_at DESC);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_data_updated_at BEFORE UPDATE ON data_sources FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_data_updated_at BEFORE UPDATE ON data_pipelines FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_data_updated_at BEFORE UPDATE ON data_transformations FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_data_updated_at BEFORE UPDATE ON data_validation_rules FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();