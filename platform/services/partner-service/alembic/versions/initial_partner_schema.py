"""Initial partner schema

Revision ID: 3c4d5e6f7g8h
Revises:
Create Date: 2026-02-12 14:00:00

"""
import uuid
from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy import Enum

# revision identifiers, used by Alembic.
revision = '3c4d5e6f7g8h'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create partnership_status enum
    op.execute("CREATE TYPE partnership_status AS ENUM ('proposed', 'accepted', 'rejected', 'active', 'terminated')")
    
    # Create companies table (if not exists - shared with user service)
    # Note: In production, this would be in a shared database or referenced from company-service
    op.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            website VARCHAR(1024),
            logo_url VARCHAR(2048),
            industry VARCHAR(100),
            sub_industries VARCHAR(1000),
            business_model TEXT,
            founded_year INTEGER,
            headquarters_country VARCHAR(100),
            headquarters_city VARCHAR(100),
            employees_count INTEGER,
            employees_range VARCHAR(50),
            funding_total VARCHAR(20),
            funding_stage VARCHAR(50),
            last_funding_date TIMESTAMPTZ,
            inn VARCHAR(12),
            ogrn VARCHAR(13),
            kpp VARCHAR(9),
            legal_name VARCHAR(255),
            tech_stack VARCHAR(2000),
            integrations VARCHAR(1000),
            api_available BOOLEAN DEFAULT FALSE,
            ai_summary TEXT,
            ai_tags VARCHAR(1000),
            embedding VARCHAR(2000),
            is_verified BOOLEAN DEFAULT FALSE,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW() ON UPDATE NOW(),
            deleted_at TIMESTAMPTZ
        )
    """)
    
    # Create partnerships table
    op.create_table(
        'partnerships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id_1', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_id_2', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.Enum('proposed', 'accepted', 'rejected', 'active', 'terminated'), nullable=False, default='proposed'),
        sa.Column('compatibility_score', sa.Float, nullable=False, default=0.0),
        sa.Column('reason', sa.Text),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('updated_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # Create unique constraints for partnerships (prevent duplicate pairs)
    op.create_index('idx_partnerships_company_1_company_2', 'partnerships', ['company_id_1', 'company_id_2'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_partnerships_company_2_company_1', 'partnerships', ['company_id_2', 'company_id_1'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    # Create partnership_metrics table
    op.create_table(
        'partnership_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('partnership_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('partnerships.id', ondelete='CASCADE'), nullable=False),
        sa.Column('metric_type', sa.String(50), nullable=False),
        sa.Column('value', sa.Float, nullable=False),
        sa.Column('unit', sa.String(20)),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # Create indexes for metrics
    op.create_index('idx_partnership_metrics_partnership_id', 'partnership_metrics', ['partnership_id'])
    op.create_index('idx_partnership_metrics_metric_type', 'partnership_metrics', ['metric_type'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_partnership_metrics_metric_type', table_name='partnership_metrics')
    op.drop_index('idx_partnership_metrics_partnership_id', table_name='partnership_metrics')
    op.drop_index('idx_partnerships_company_2_company_1', table_name='partnerships')
    op.drop_index('idx_partnerships_company_1_company_2', table_name='partnerships')

    # Drop tables
    op.drop_table('partnership_metrics')
    op.drop_table('partnerships')

    # Drop enums
    op.execute("DROP TYPE partnership_status")