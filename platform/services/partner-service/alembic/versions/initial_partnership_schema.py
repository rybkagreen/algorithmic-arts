"""Initial partnership schema

Revision ID: 3a4b5c6d7e8f
Revises: 
Create Date: 2026-02-12 12:00:00

"""
import uuid
from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3a4b5c6d7e8f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create partnerships table
    op.create_table(
        'partnerships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_a_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_b_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('compatibility_score', sa.Numeric(3, 2)),
        sa.Column('match_reasons', postgresql.ARRAY(sa.String(255))),
        sa.Column('synergy_areas', postgresql.ARRAY(sa.String(255))),
        sa.Column('analysis_method', sa.String(100)),
        sa.Column('analyzed_by_agent', sa.String(100)),
        sa.Column('ai_explanation', sa.Text),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('contacted_at', sa.DateTime(timezone=True)),
        sa.Column('partnership_started_at', sa.DateTime(timezone=True)),
        sa.Column('deal_value', sa.Numeric(15, 2)),
        sa.Column('revenue_generated', sa.Numeric(15, 2)),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # Create outreach_messages table
    op.create_table(
        'outreach_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('partnership_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('message_text', sa.Text, nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('response_received', sa.Boolean, default=False),
        sa.Column('response_text', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
    )

    # Add foreign key constraints
    op.create_foreign_key('fk_partnerships_company_a_id', 'partnerships', 'companies', ['company_a_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_partnerships_company_b_id', 'partnerships', 'companies', ['company_b_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_outreach_messages_partnership_id', 'outreach_messages', 'partnerships', ['partnership_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Drop foreign key constraints first
    op.drop_constraint('fk_outreach_messages_partnership_id', 'outreach_messages')
    op.drop_constraint('fk_partnerships_company_b_id', 'partnerships')
    op.drop_constraint('fk_partnerships_company_a_id', 'partnerships')

    # Drop tables
    op.drop_table('outreach_messages')
    op.drop_table('partnerships')