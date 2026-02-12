"""Initial notification service schema

Revision ID: 6f7a8b9c0d1e
Revises: 
Create Date: 2026-02-12 11:15:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6f7a8b9c0d1e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notification_channels table
    op.create_table('notification_channels',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create notification_templates table
    op.create_table('notification_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('channel_type', sa.String(length=50), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('variables', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('channel_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='queued'),
        sa.Column('recipient', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('sent_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('delivered_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('read_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['notification_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['channel_id'], ['notification_channels.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create notification_schedules table
    op.create_table('notification_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('schedule_type', sa.String(length=50), nullable=False),
        sa.Column('scheduled_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('cron_expression', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['template_id'], ['notification_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create notification_events table
    op.create_table('notification_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=True, default=False),
        sa.Column('processed_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create notification_delivery_logs table
    op.create_table('notification_delivery_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('channel_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_notification_channels_type', 'notification_channels', ['type'])
    op.create_index('idx_notification_channels_deleted_at', 'notification_channels', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NOT NULL'))
    op.create_index('idx_notification_templates_channel_type', 'notification_templates', ['channel_type'])
    op.create_index('idx_notification_templates_deleted_at', 'notification_templates', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NOT NULL'))
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_template_id', 'notifications', ['template_id'])
    op.create_index('idx_notifications_channel_id', 'notifications', ['channel_id'])
    op.create_index('idx_notifications_status', 'notifications', ['status'])
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'], postgresql_where=sa.text('created_at DESC'))
    op.create_index('idx_notification_schedules_user_id', 'notification_schedules', ['user_id'])
    op.create_index('idx_notification_schedules_scheduled_at', 'notification_schedules', ['scheduled_at'])
    op.create_index('idx_notification_schedules_is_active', 'notification_schedules', ['is_active'])
    op.create_index('idx_notification_events_event_type', 'notification_events', ['event_type'])
    op.create_index('idx_notification_events_processed', 'notification_events', ['processed'])
    op.create_index('idx_notification_delivery_logs_notification_id', 'notification_delivery_logs', ['notification_id'])
    op.create_index('idx_notification_delivery_logs_status', 'notification_delivery_logs', ['status'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_notification_delivery_logs_status', table_name='notification_delivery_logs')
    op.drop_index('idx_notification_delivery_logs_notification_id', table_name='notification_delivery_logs')
    op.drop_index('idx_notification_events_processed', table_name='notification_events')
    op.drop_index('idx_notification_events_event_type', table_name='notification_events')
    op.drop_index('idx_notification_schedules_is_active', table_name='notification_schedules')
    op.drop_index('idx_notification_schedules_scheduled_at', table_name='notification_schedules')
    op.drop_index('idx_notification_schedules_user_id', table_name='notification_schedules')
    op.drop_index('idx_notifications_created_at', table_name='notifications')
    op.drop_index('idx_notifications_status', table_name='notifications')
    op.drop_index('idx_notifications_channel_id', table_name='notifications')
    op.drop_index('idx_notifications_template_id', table_name='notifications')
    op.drop_index('idx_notifications_user_id', table_name='notifications')
    op.drop_index('idx_notification_templates_deleted_at', table_name='notification_templates')
    op.drop_index('idx_notification_templates_channel_type', table_name='notification_templates')
    op.drop_index('idx_notification_channels_deleted_at', table_name='notification_channels')
    op.drop_index('idx_notification_channels_type', table_name='notification_channels')
    
    # Drop tables
    op.drop_table('notification_delivery_logs')
    op.drop_table('notification_events')
    op.drop_table('notification_schedules')
    op.drop_table('notifications')
    op.drop_table('notification_templates')
    op.drop_table('notification_channels')