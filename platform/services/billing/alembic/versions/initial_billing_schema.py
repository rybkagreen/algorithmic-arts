"""Initial billing schema

Revision ID: 5a6b7c8d9e0f
Revises: 
Create Date: 2026-02-12 14:00:00

"""
import uuid
from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5a6b7c8d9e0f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cancel_at_period_end', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
    )

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), default="RUB"),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('external_payment_id', sa.String(255)),
        sa.Column('paid_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
    )

    # Add foreign key constraints
    op.create_foreign_key('fk_subscriptions_user_id', 'subscriptions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_payments_subscription_id', 'payments', 'subscriptions', ['subscription_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Drop foreign key constraints first
    op.drop_constraint('fk_payments_subscription_id', 'payments')
    op.drop_constraint('fk_subscriptions_user_id', 'subscriptions')

    # Drop tables
    op.drop_table('payments')
    op.drop_table('subscriptions')