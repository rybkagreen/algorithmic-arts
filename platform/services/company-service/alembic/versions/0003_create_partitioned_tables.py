"""Create partitioned tables for company_updates and company_metrics

Revision ID: 0003_create_partitioned_tables
Revises: 0002_event_store
Create Date: 2026-02-12 10:00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0003_create_partitioned_tables'
down_revision = '0002_event_store'
branch_labels = None
depends_on = None


def upgrade():
    # Create company_updates table with range partitioning by created_at (monthly)
    op.execute("""
        CREATE TABLE company_updates (
            id UUID PRIMARY KEY,
            company_id UUID NOT NULL,
            update_type VARCHAR(50) NOT NULL,
            old_value JSONB,
            new_value JSONB,
            changed_fields TEXT[],
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL
        ) PARTITION BY RANGE (created_at);
    """)
    
    # Create partitions for company_updates (last 12 months + future)
    for i in range(-12, 13):
        month_start = f"2026-{i+12:02d}-01"
        month_end = f"2026-{i+13:02d}-01"
        partition_name = f"company_updates_{i+12:02d}"
        op.execute(f"""
            CREATE TABLE {partition_name} PARTITION OF company_updates
            FOR VALUES FROM ('{month_start}') TO ('{month_end}');
        """)
    
    # Create index on company_id for faster lookups
    op.execute("CREATE INDEX idx_company_updates_company_id ON company_updates (company_id);")
    
    # Create company_metrics table with hash partitioning by company_id
    op.execute("""
        CREATE TABLE company_metrics (
            id UUID PRIMARY KEY,
            company_id UUID NOT NULL,
            metric_type VARCHAR(50) NOT NULL,
            value NUMERIC NOT NULL,
            unit VARCHAR(20),
            period_start TIMESTAMP WITH TIME ZONE NOT NULL,
            period_end TIMESTAMP WITH TIME ZONE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL
        ) PARTITION BY HASH (company_id);
    """)
    
    # Create 16 partitions for company_metrics (hash partitioning)
    for i in range(16):
        partition_name = f"company_metrics_p{i}"
        op.execute(f"""
            CREATE TABLE {partition_name} PARTITION OF company_metrics
            FOR VALUES WITH (MODULUS 16, REMAINDER {i});
        """)
    
    # Create indexes on company_id and metric_type
    op.execute("CREATE INDEX idx_company_metrics_company_id ON company_metrics (company_id);")
    op.execute("CREATE INDEX idx_company_metrics_metric_type ON company_metrics (metric_type);")


def downgrade():
    # Drop partitions and main tables
    op.execute("DROP TABLE IF EXISTS company_updates;")
    op.execute("DROP TABLE IF EXISTS company_metrics;")