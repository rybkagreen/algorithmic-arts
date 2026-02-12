-- CRM Database Schema

-- CRM connections table
CREATE TABLE crm_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    crm_type VARCHAR(50) NOT NULL CHECK (crm_type IN ('amocrm', 'bitrix24', 'salesforce')),
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMPTZ,
    account_subdomain VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- CRM sync logs table
CREATE TABLE crm_sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID NOT NULL REFERENCES crm_connections(id) ON DELETE CASCADE,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('to_crm', 'from_crm')),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    synced_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_crm_connections_user_id ON crm_connections(user_id);
CREATE INDEX idx_crm_connections_crm_type ON crm_connections(crm_type);
CREATE INDEX idx_crm_connections_deleted_at ON crm_connections(deleted_at) WHERE deleted_at IS NOT NULL;
CREATE INDEX idx_crm_sync_logs_connection_id ON crm_sync_logs(connection_id);
CREATE INDEX idx_crm_sync_logs_entity_type ON crm_sync_logs(entity_type);
CREATE INDEX idx_crm_sync_logs_synced_at ON crm_sync_logs(synced_at);
CREATE INDEX idx_crm_sync_logs_status ON crm_sync_logs(status);

-- Triggers
CREATE TRIGGER update_crm_updated_at BEFORE UPDATE ON crm_connections FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_crm_updated_at BEFORE UPDATE ON crm_sync_logs FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();