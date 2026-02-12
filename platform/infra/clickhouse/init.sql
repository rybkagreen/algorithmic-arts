-- ClickHouse initialization script for ALGORITHMIC ARTS platform

-- Create databases
CREATE DATABASE IF NOT EXISTS algorithmic_arts;

-- Use the database
USE algorithmic_arts;

-- Create tables (from schema.sql)
-- Partnerships analytics table
CREATE TABLE IF NOT EXISTS partnerships_analytics
(
    id UUID,
    company_id_1 UUID,
    company_id_2 UUID,
    status Enum('proposed', 'accepted', 'rejected', 'active', 'terminated'),
    compatibility_score Float32,
    created_at DateTime,
    updated_at DateTime,
    created_by_user_id UUID,
    updated_by_user_id UUID,
    industry_1 String,
    industry_2 String,
    employees_count_1 Int32,
    employees_count_2 Int32,
    tech_stack_overlap Float32,
    market_overlap Float32,
    geographic_proximity Float32,
    no_direct_competition Float32,
    feature_complementarity Float32
)
ENGINE = MergeTree()
ORDER BY (created_at, company_id_1, company_id_2)
PARTITION BY toYYYYMM(created_at);

-- Companies analytics table
CREATE TABLE IF NOT EXISTS companies_analytics
(
    id UUID,
    name String,
    slug String,
    industry String,
    founded_year Int32,
    headquarters_country String,
    employees_count Int32,
    employees_range String,
    funding_stage String,
    tech_stack Array(String),
    ai_tags Array(String),
    is_verified Bool,
    view_count Int32,
    created_at DateTime,
    updated_at DateTime,
    embedding Array(Float32)
)
ENGINE = MergeTree()
ORDER BY (created_at, industry, employees_count)
PARTITION BY toYYYYMM(created_at);

-- Users analytics table
CREATE TABLE IF NOT EXISTS users_analytics
(
    id UUID,
    email String,
    full_name String,
    company_id UUID,
    role Enum('free_user', 'paid_user', 'company_admin', 'platform_admin'),
    is_active Bool,
    is_verified Bool,
    created_at DateTime,
    updated_at DateTime,
    last_login_at DateTime
)
ENGINE = MergeTree()
ORDER BY (created_at, company_id, role)
PARTITION BY toYYYYMM(created_at);

-- Partnership metrics table
CREATE TABLE IF NOT EXISTS partnership_metrics
(
    id UUID,
    partnership_id UUID,
    metric_type String,
    value Float32,
    unit String,
    period_start DateTime,
    period_end DateTime,
    created_at DateTime
)
ENGINE = MergeTree()
ORDER BY (period_start, partnership_id, metric_type)
PARTITION BY toYYYYMM(period_start);

-- Materialized views
CREATE MATERIALIZED VIEW IF NOT EXISTS partnerships_by_status_mv
TO partnerships_by_status
AS SELECT
    status,
    count() as count,
    avg(compatibility_score) as avg_compatibility,
    toStartOfDay(created_at) as day
FROM partnerships_analytics
GROUP BY status, day;

CREATE MATERIALIZED VIEW IF NOT EXISTS companies_by_industry_mv
TO companies_by_industry
AS SELECT
    industry,
    count() as count,
    avg(employees_count) as avg_employees,
    toStartOfDay(created_at) as day
FROM companies_analytics
GROUP BY industry, day;

-- Insert sample data for testing
INSERT INTO partnerships_analytics VALUES
('12345678-1234-5678-1234-567812345678', '87654321-4321-8765-4321-876543216789', '12345678-1234-5678-1234-567812345678', 'active', 0.85, now(), now(), '11111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'Software', 'AI', 50, 200, 0.9, 0.7, 0.8, 0.9, 0.8),

('23456789-2345-6789-2345-678923456789', '98765432-2109-8765-4321-987654321098', '23456789-2345-6789-2345-678923456789', 'proposed', 0.65, now(), now(), '22222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 'Fintech', 'Healthcare', 100, 150, 0.6, 0.5, 0.7, 0.8, 0.6);

INSERT INTO companies_analytics VALUES
('87654321-4321-8765-4321-876543216789', 'TechCorp', 'techcorp', 'Software', 2015, 'RU', 200, '100-500', 'Series B', ['Python', 'PostgreSQL', 'Kafka'], ['AI', 'ML'], true, 1500, now(), now(), [0.1, 0.2, 0.3, 0.4, 0.5]),
('98765432-2109-8765-4321-987654321098', 'HealthAI', 'healthai', 'Healthcare', 2018, 'RU', 150, '50-200', 'Series A', ['JavaScript', 'MongoDB', 'TensorFlow'], ['Healthcare', 'AI'], true, 800, now(), now(), [0.2, 0.3, 0.4, 0.5, 0.6]);

INSERT INTO users_analytics VALUES
('11111111-1111-1111-1111-111111111111', 'admin@algorithmic-arts.ru', 'Admin User', '87654321-4321-8765-4321-876543216789', 'platform_admin', true, true, now(), now(), now()),
('22222222-2222-2222-2222-222222222222', 'user@techcorp.ru', 'TechCorp Admin', '87654321-4321-8765-4321-876543216789', 'company_admin', true, true, now(), now(), now());