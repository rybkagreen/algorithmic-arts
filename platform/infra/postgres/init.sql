-- Расширения PostgreSQL 17
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_cron";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Citus (шардирование — только если включён)
-- CREATE EXTENSION IF NOT EXISTS "citus";

-- Shared триггер для auto-update updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Макрос для создания триггера на таблицу
-- Использование: SELECT create_updated_at_trigger('companies');
CREATE OR REPLACE FUNCTION create_updated_at_trigger(table_name TEXT)
RETURNS void AS $$
BEGIN
    EXECUTE format(
        'CREATE TRIGGER set_updated_at
         BEFORE UPDATE ON %I
         FOR EACH ROW EXECUTE FUNCTION set_updated_at()',
        table_name
    );
END;
$$ LANGUAGE plpgsql;