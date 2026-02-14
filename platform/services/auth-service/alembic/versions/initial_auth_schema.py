"""Initial auth schema

Revision ID: 1a2b3c4d5e6f
Revises:
Create Date: 2026-02-12 12:00:00

"""
import uuid
from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_role enum
    op.execute("CREATE TYPE user_role AS ENUM ('free_user', 'paid_user', 'company_admin', 'platform_admin')")
    
    # Create oauth_provider enum
    op.execute("CREATE TYPE oauth_provider AS ENUM ('yandex', 'google', 'vk')")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(72), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('company_name', sa.String(255)),
        sa.Column('role', sa.Enum('free_user', 'paid_user', 'company_admin', 'platform_admin'), nullable=False, default='free_user'),
        sa.Column('is_active', sa.Boolean, nullable=False, default=False),
        sa.Column('is_verified', sa.Boolean, nullable=False, default=False),
        sa.Column('totp_secret', sa.String(32)),
        sa.Column('totp_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True)),
        sa.Column('failed_login_count', sa.Integer, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # Create indexes for users
    op.create_index('idx_users_email', 'users', ['email'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_users_role', 'users', ['role'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_users_created_at', 'users', ['created_at'], postgresql_ops={'created_at': 'DESC'})

    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for refresh_tokens
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'], postgresql_where=sa.text('revoked_at IS NULL'))

    # Create oauth_connections table
    op.create_table(
        'oauth_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.Enum('yandex', 'google', 'vk'), nullable=False),
        sa.Column('external_id', sa.String(255), nullable=False),
        sa.Column('access_token', sa.Text),
        sa.Column('refresh_token', sa.Text),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('provider', 'external_id'),
    )

    # Create indexes for oauth_connections
    op.create_index('idx_oauth_user_id', 'oauth_connections', ['user_id'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_oauth_user_id', table_name='oauth_connections')
    op.drop_index('idx_refresh_tokens_expires_at', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_email', table_name='users')

    # Drop tables
    op.drop_table('oauth_connections')
    op.drop_table('refresh_tokens')
    op.drop_table('users')

    # Drop enums
    op.execute("DROP TYPE oauth_provider")
    op.execute("DROP TYPE user_role")