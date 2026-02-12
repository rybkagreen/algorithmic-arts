"""Initial auth schema

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2026-02-12 10:00:00

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
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('company_name', sa.String(255)),
        sa.Column('role', sa.String(50)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('two_factor_enabled', sa.Boolean, default=False),
        sa.Column('two_factor_secret', sa.String(255)),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.Text, nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
    )

    # Create oauth_connections table
    op.create_table(
        'oauth_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('external_id', sa.String(255), nullable=False),
        sa.Column('access_token', sa.Text),
        sa.Column('refresh_token', sa.Text),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
    )

    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
    )

    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow),
    )

    # Create role_permissions table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
    )

    # Create user_roles table
    op.create_table(
        'user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
    )

    # Add foreign key constraints
    op.create_foreign_key('fk_sessions_user_id', 'sessions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_oauth_connections_user_id', 'oauth_connections', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_role_permissions_role_id', 'role_permissions', 'roles', ['role_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_role_permissions_permission_id', 'role_permissions', 'permissions', ['permission_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_user_roles_user_id', 'user_roles', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_user_roles_role_id', 'user_roles', 'roles', ['role_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Drop foreign key constraints first
    op.drop_constraint('fk_user_roles_role_id', 'user_roles')
    op.drop_constraint('fk_user_roles_user_id', 'user_roles')
    op.drop_constraint('fk_role_permissions_permission_id', 'role_permissions')
    op.drop_constraint('fk_role_permissions_role_id', 'role_permissions')
    op.drop_constraint('fk_oauth_connections_user_id', 'oauth_connections')
    op.drop_constraint('fk_sessions_user_id', 'sessions')

    # Drop tables
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    op.drop_table('permissions')
    op.drop_table('oauth_connections')
    op.drop_table('sessions')
    op.drop_table('users')