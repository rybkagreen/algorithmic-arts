"""Initial user service schema

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2026-02-12 10:00:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_profiles table
    op.create_table('user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('avatar_url', sa.String(length=2048), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('job_title', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('timezone', sa.String(length=100), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('theme_preference', sa.String(length=20), nullable=True, default='light'),
        sa.Column('email_notifications', sa.Boolean(), nullable=True, default=True),
        sa.Column('push_notifications', sa.Boolean(), nullable=True, default=True),
        sa.Column('sms_notifications', sa.Boolean(), nullable=True, default=False),
        sa.Column('two_factor_method', sa.String(length=20), nullable=True),
        sa.Column('last_active_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create user_preferences table
    op.create_table('user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'category', 'key')
    )
    
    # Create user_contacts table
    op.create_table('user_contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_type', sa.String(length=20), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=True, default=False),
        sa.Column('verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_activity_logs table
    op.create_table('user_activity_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_bookmarks table
    op.create_table('user_bookmarks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bookmark_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'bookmark_type', 'resource_id')
    )
    
    # Create indexes
    op.create_index('idx_user_profiles_user_id', 'user_profiles', ['user_id'])
    op.create_index('idx_user_profiles_deleted_at', 'user_profiles', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NOT NULL'))
    op.create_index('idx_user_preferences_user_id', 'user_preferences', ['user_id'])
    op.create_index('idx_user_preferences_category_key', 'user_preferences', ['category', 'key'])
    op.create_index('idx_user_contacts_user_id', 'user_contacts', ['user_id'])
    op.create_index('idx_user_contacts_type_value', 'user_contacts', ['contact_type', 'value'])
    op.create_index('idx_user_activity_logs_user_id', 'user_activity_logs', ['user_id'])
    op.create_index('idx_user_activity_logs_created_at', 'user_activity_logs', ['created_at'], postgresql_where=sa.text('created_at DESC'))
    op.create_index('idx_user_bookmarks_user_id', 'user_bookmarks', ['user_id'])
    op.create_index('idx_user_bookmarks_resource_id', 'user_bookmarks', ['resource_id'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_user_bookmarks_resource_id', table_name='user_bookmarks')
    op.drop_index('idx_user_bookmarks_user_id', table_name='user_bookmarks')
    op.drop_index('idx_user_activity_logs_created_at', table_name='user_activity_logs')
    op.drop_index('idx_user_activity_logs_user_id', table_name='user_activity_logs')
    op.drop_index('idx_user_contacts_type_value', table_name='user_contacts')
    op.drop_index('idx_user_contacts_user_id', table_name='user_contacts')
    op.drop_index('idx_user_preferences_category_key', table_name='user_preferences')
    op.drop_index('idx_user_preferences_user_id', table_name='user_preferences')
    op.drop_index('idx_user_profiles_deleted_at', table_name='user_profiles')
    op.drop_index('idx_user_profiles_user_id', table_name='user_profiles')
    
    # Drop tables
    op.drop_table('user_bookmarks')
    op.drop_table('user_activity_logs')
    op.drop_table('user_contacts')
    op.drop_table('user_preferences')
    op.drop_table('user_profiles')