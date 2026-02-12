-- Search Service Database Schema

-- Search indexes table (metadata about Elasticsearch indices)
CREATE TABLE search_indexes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    document_type VARCHAR(50) NOT NULL, -- 'company', 'partnership', 'user', 'crm_contact'
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'inactive', 'rebuilding', 'error'
    mapping JSONB, -- Elasticsearch mapping configuration
    settings JSONB, -- Elasticsearch index settings
    total_documents INTEGER DEFAULT 0,
    last_updated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Search queries table (for query logging and analytics)
CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    index_name VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    query_params JSONB,
    results_count INTEGER DEFAULT 0,
    execution_time_ms INTEGER DEFAULT 0,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Search suggestions table (for autocomplete and suggestions)
CREATE TABLE search_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    index_name VARCHAR(255) NOT NULL,
    term VARCHAR(255) NOT NULL,
    document_count INTEGER DEFAULT 0,
    score NUMERIC(5,3) DEFAULT 1.0,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Search relevance feedback table (for improving search quality)
CREATE TABLE search_relevance_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES search_queries(id) ON DELETE CASCADE,
    document_id UUID NOT NULL,
    relevance_score SMALLINT NOT NULL, -- -1 (irrelevant), 0 (neutral), 1 (relevant)
    feedback_type VARCHAR(20) NOT NULL, -- 'click', 'rating', 'explicit'
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Search facets table
CREATE TABLE search_facets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    index_name VARCHAR(255) NOT NULL,
    facet_name VARCHAR(100) NOT NULL,
    facet_type VARCHAR(50) NOT NULL, -- 'term', 'range', 'date_range', 'histogram'
    config JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_search_indexes_document_type ON search_indexes(document_type);
CREATE INDEX idx_search_indexes_status ON search_indexes(status);
CREATE INDEX idx_search_queries_user_id ON search_queries(user_id);
CREATE INDEX idx_search_queries_index_name ON search_queries(index_name);
CREATE INDEX idx_search_queries_created_at ON search_queries(created_at DESC);
CREATE INDEX idx_search_suggestions_index_name_term ON search_suggestions(index_name, term);
CREATE INDEX idx_search_suggestions_score ON search_suggestions(score DESC);
CREATE INDEX idx_search_relevance_feedback_query_id ON search_relevance_feedback(query_id);
CREATE INDEX idx_search_relevance_feedback_document_id ON search_relevance_feedback(document_id);
CREATE INDEX idx_search_facets_index_name ON search_facets(index_name);
CREATE INDEX idx_search_facets_facet_name ON search_facets(facet_name);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_search_updated_at BEFORE UPDATE ON search_indexes FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_search_updated_at BEFORE UPDATE ON search_suggestions FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_search_updated_at BEFORE UPDATE ON search_facets FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();