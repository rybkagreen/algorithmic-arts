"""Initial user schema

Revision ID: 2b3c4d5e6f7g
Revises:
Create Date: 2026-02-12 13:00:00

"""
import uuid
from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy import Enum

# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7g'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_role enum
    op.execute("CREATE TYPE user_role AS ENUM ('free_user', 'paid_user', 'company_admin', 'platform_admin')")
    
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
        sa.Column('sub_industries', sa.String(1000)),  # JSON array stored as string
        sa.Column('business_model', sa.Text),
        sa.Column('founded_year', sa.Integer),
        sa.Column('headquarters_country', sa.String(100)),
        sa.Column('headquarters_city', sa.String(100)),
        sa.Column('employees_count', sa.Integer),
        sa.Column('employees_range', sa.String(50)),
        sa.Column('funding_total', sa.String(20)),  # Decimal stored as string
        sa.Column('funding_stage', sa.String(50)),
        sa.Column('last_funding_date', sa.DateTime(timezone=True)),
        sa.Column('inn', sa.String(12)),
        sa.Column('ogrn', sa.String(13)),
        sa.Column('kpp', sa.String(9)),
        sa.Column('legal_name', sa.String(255)),
        sa.Column('tech_stack', sa.String(2000)),  # JSON stored as string
        sa.Column('integrations', sa.String(1000)),  # JSON array stored as string
        sa.Column('api_available', sa.Boolean, default=False),
        sa.Column('ai_summary', sa.Text),
        sa.Column('ai_tags', sa.String(1000)),  # JSON array stored as string
        sa.Column('embedding', sa.String(2000)),  # Vector stored as string
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('view_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # Create indexes for companies
    op.create_index('idx_companies_slug', 'companies', ['slug'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_companies_industry', 'companies', ['industry'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_companies_created_at', 'companies', ['created_at'], postgresql_ops={'created_at': 'DESC'})

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='SET NULL')),
        sa.Column('role', sa.Enum('free_user', 'paid_user', 'company_admin', 'platform_admin'), nullable=False, default='free_user'),
        sa.Column('is_active', sa.Boolean, nullable=False, default=False),
        sa.Column('is_verified', sa.Boolean, nullable=False, default=False),
        sa.Column('totp_secret', sa.String(32)),  # NULL = 2FA отключена
        sa.Column('totp_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True)),
        sa.Column('failed_login_count', sa.Integer, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # Create indexes for users
    op.create_index('idx_users_email', 'users', ['email'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_users_company_id', 'users', ['company_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_users_role', 'users', ['role'], postgresql_where=sa.text('deleted_at IS NULL'))


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_company_id', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_index('idx_companies_created_at', table_name='companies')
    op.drop_index('idx_companies_industry', table_name='companies')
    op.drop_index('idx_companies_slug', table_name='companies')

    # Drop tables
    op.drop_table('users')
    op.drop_table('companies')

    # Drop enums
    op.execute("DROP TYPE user_role")