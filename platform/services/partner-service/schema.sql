-- Partnership Database Schema

-- Partnerships table
CREATE TABLE partnerships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_a_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    company_b_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    compatibility_score NUMERIC(3,2),
    match_reasons TEXT[],
    synergy_areas TEXT[],
    analysis_method VARCHAR(100),
    analyzed_by_agent VARCHAR(100),
    ai_explanation TEXT,
    status VARCHAR(50) NOT NULL,
    contacted_at TIMESTAMPTZ,
    partnership_started_at TIMESTAMPTZ,
    deal_value NUMERIC(15,2),
    revenue_generated NUMERIC(15,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Outreach messages table
CREATE TABLE outreach_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partnership_id UUID NOT NULL REFERENCES partnerships(id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    sent_at TIMESTAMPTZ NOT NULL,
    response_received BOOLEAN DEFAULT FALSE,
    response_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_partnerships_company_a_id ON partnerships(company_a_id);
CREATE INDEX idx_partnerships_company_b_id ON partnerships(company_b_id);
CREATE INDEX idx_partnerships_status ON partnerships(status);
CREATE INDEX idx_partnerships_compatibility_score ON partnerships(compatibility_score);
CREATE INDEX idx_partnerships_deleted_at ON partnerships(deleted_at) WHERE deleted_at IS NOT NULL;
CREATE INDEX idx_outreach_messages_partnership_id ON outreach_messages(partnership_id);
CREATE INDEX idx_outreach_messages_sent_at ON outreach_messages(sent_at);

-- Triggers
CREATE TRIGGER update_partnership_updated_at BEFORE UPDATE ON partnerships FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_partnership_updated_at BEFORE UPDATE ON outreach_messages FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();