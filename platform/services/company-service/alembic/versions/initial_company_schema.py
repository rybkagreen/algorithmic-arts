"""Initial company schema

Revision ID: 2a3b4c5d6e7f
Revises: 
Create Date: 2026-02-12 11:00:00

"""
import uuid
from datetime import date, datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2a3b4c5d6e7f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('website', sa.String(1024)),
        sa.Column('logo_url', sa.String(2048)),
        sa.Column('industry', sa.String(100)),
        sa.Column('sub_industries', postgresql.ARRAY(sa.String(100))),
        sa.Column('business_model', sa.Text),
        sa.Column('founded_year', sa.Integer),
        sa.Column('headquarters_country', sa.String(100)),
        sa.Column('headquarters_city', sa.String(100)),
        sa.Column('employees_count', sa.Integer),
        sa.Column('employees_range', sa.String(50)),
        sa.Column('funding_total', sa.Numeric(15, 2)),
        sa.Column('funding_stage', sa.String(50)),
        sa.Column('last_funding_date', sa.Date),
        sa.Column('inn', sa.String(12)),
        sa.Column('ogrn', sa.String(13)),
        sa.Column('kpp', sa.String(9)),
        sa.Column('legal_name', sa.String(255)),
        sa.Column('tech_stack', postgresql.JSON),
        sa.Column('integrations', postgresql.ARRAY(sa.String(100))),
        sa.Column('api_available', sa.Boolean, default=False),
        sa.Column('ai_summary', sa.Text),
        sa.Column('ai_tags', postgresql.ARRAY(sa.String(50))),
        sa.Column('embedding', postgresql VECTOR(1536)),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('view_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # Create company_updates table (partitioned)
    op.execute("""
    CREATE TABLE company_updates (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL,
        update_type VARCHAR(50) NOT NULL,
        title VARCHAR(500) NOT NULL,
        content TEXT,
        source_url VARCHAR(2048),
        published_at TIMESTAMPTZ NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    ) PARTITION BY RANGE (published_at);
    """)

    # Create partitions for company_updates
    op.execute("""
    CREATE TABLE company_updates_2025 PARTITION OF company_updates
        FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
    """)
    
    op.execute("""
    CREATE TABLE company_updates_2026 PARTITION OF company_updates
        FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
    """)

    # Create company_metrics table (partitioned)
    op.execute("""
    CREATE TABLE company_metrics (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL,
        metric_name VARCHAR(100) NOT NULL,
        metric_value NUMERIC(15,2) NOT NULL,
        measured_at TIMESTAMPTZ NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    ) PARTITION BY RANGE (measured_at);
    """)

    # Create partitions for company_metrics
    op.execute("""
    CREATE TABLE company_metrics_2026_01 PARTITION OF company_metrics
        FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
    """)
    
    op.execute("""
    CREATE TABLE company_metrics_2026_02 PARTITION OF company_metrics
        FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
    """)

    # Add foreign key constraints
    op.create_foreign_key('fk_company_updates_company_id', 'company_updates', 'companies', ['company_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_company_metrics_company_id', 'company_metrics', 'companies', ['company_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Drop foreign key constraints first
    op.drop_constraint('fk_company_metrics_company_id', 'company_metrics')
    op.drop_constraint('fk_company_updates_company_id', 'company_updates')

    # Drop partitioned tables
    op.execute("DROP TABLE company_updates_2025")
    op.execute("DROP TABLE company_updates_2026")
    op.execute("DROP TABLE company_updates")
    
    op.execute("DROP TABLE company_metrics_2026_01")
    op.execute("DROP TABLE company_metrics_2026_02")
    op.execute("DROP TABLE company_metrics")

    # Drop companies table
    op.drop_table('companies')