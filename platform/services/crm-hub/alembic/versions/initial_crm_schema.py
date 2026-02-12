"""Initial CRM schema

Revision ID: 4a5b6c7d8e9f
Revises: 
Create Date: 2026-02-12 13:00:00

"""
import uuid
from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4a5b6c7d8e9f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create crm_connections table
    op.create_table(
        'crm_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('crm_type', sa.Enum('amocrm', 'bitrix24', 'salesforce'), nullable=False),
        sa.Column('access_token', sa.Text, nullable=False),
        sa.Column('refresh_token', sa.Text),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('account_subdomain', sa.String(255)),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # Create crm_sync_logs table
    op.create_table(
        'crm_sync_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('direction', sa.Enum('to_crm', 'from_crm'), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
    )

    # Add foreign key constraints
    op.create_foreign_key('fk_crm_connections_user_id', 'crm_connections', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_crm_sync_logs_connection_id', 'crm_sync_logs', 'crm_connections', ['connection_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Drop foreign key constraints first
    op.drop_constraint('fk_crm_sync_logs_connection_id', 'crm_sync_logs')
    op.drop_constraint('fk_crm_connections_user_id', 'crm_connections')

    # Drop tables
    op.drop_table('crm_sync_logs')
    op.drop_table('crm_connections')