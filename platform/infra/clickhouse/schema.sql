-- ClickHouse schema for ALGORITHMIC ARTS platform analytics

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

-- Kafka integration tables (for streaming data)
CREATE TABLE IF NOT EXISTS kafka_partnership_events
(
    event_id UUID,
    event_type String,
    aggregate_id UUID,
    payload String,
    occurred_at DateTime,
    topic String
)
ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'partnership.events',
    kafka_group_name = 'clickhouse-consumer',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 1;

CREATE TABLE IF NOT EXISTS partnerships_from_kafka
(
    event_id UUID,
    event_type String,
    aggregate_id UUID,
    payload String,
    occurred_at DateTime,
    topic String
)
ENGINE = MergeTree()
ORDER BY (occurred_at, aggregate_id)
PARTITION BY toYYYYMM(occurred_at);

CREATE MATERIALIZED VIEW IF NOT EXISTS partnerships_from_kafka_mv TO partnerships_analytics
AS SELECT
    JSONExtractString(payload, 'id') AS id,
    JSONExtractString(payload, 'company_id_1') AS company_id_1,
    JSONExtractString(payload, 'company_id_2') AS company_id_2,
    JSONExtractString(payload, 'status') AS status,
    JSONExtractFloat(payload, 'compatibility_score') AS compatibility_score,
    occurred_at AS created_at,
    occurred_at AS updated_at,
    JSONExtractString(payload, 'created_by_user_id') AS created_by_user_id,
    JSONExtractString(payload, 'updated_by_user_id') AS updated_by_user_id,
    JSONExtractString(JSONExtractString(payload, 'company_1'), 'industry') AS industry_1,
    JSONExtractString(JSONExtractString(payload, 'company_2'), 'industry') AS industry_2,
    JSONExtractInt(JSONExtractString(payload, 'company_1'), 'employees_count') AS employees_count_1,
    JSONExtractInt(JSONExtractString(payload, 'company_2'), 'employees_count') AS employees_count_2,
    JSONExtractFloat(payload, 'factors', 'tech_stack_overlap') AS tech_stack_overlap,
    JSONExtractFloat(payload, 'factors', 'market_overlap') AS market_overlap,
    JSONExtractFloat(payload, 'factors', 'geographic_proximity') AS geographic_proximity,
    JSONExtractFloat(payload, 'factors', 'no_direct_competition') AS no_direct_competition,
    JSONExtractFloat(payload, 'factors', 'feature_complementarity') AS feature_complementarity
FROM partnerships_from_kafka;