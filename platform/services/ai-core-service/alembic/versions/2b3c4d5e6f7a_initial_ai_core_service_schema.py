"""Initial AI core service schema

Revision ID: 2b3c4d5e6f7a
Revises: 
Create Date: 2026-02-12 10:15:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ai_models table
    op.create_table('ai_models',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model_id', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create ai_analyses table
    op.create_table('ai_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_type', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('completed_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create ai_embeddings table
    op.create_table('ai_embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create ai_prompts table
    op.create_table('ai_prompts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('variables', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('temperature', sa.Numeric(precision=3, scale=2), nullable=True, default=0.7),
        sa.Column('max_tokens', sa.Integer(), nullable=True, default=1000),
        sa.Column('is_system', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create ai_chat_sessions table
    op.create_table('ai_chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create ai_chat_messages table
    op.create_table('ai_chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['session_id'], ['ai_chat_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_ai_models_provider', 'ai_models', ['provider'])
    op.create_index('idx_ai_models_deleted_at', 'ai_models', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NOT NULL'))
    op.create_index('idx_ai_analyses_resource_type_id', 'ai_analyses', ['resource_type', 'resource_id'])
    op.create_index('idx_ai_analyses_status', 'ai_analyses', ['status'])
    op.create_index('idx_ai_analyses_created_at', 'ai_analyses', ['created_at'], postgresql_where=sa.text('created_at DESC'))
    op.create_index('idx_ai_embeddings_resource_type_id', 'ai_embeddings', ['resource_type', 'resource_id'])
    op.create_index('idx_ai_prompts_category', 'ai_prompts', ['category'])
    op.create_index('idx_ai_prompts_deleted_at', 'ai_prompts', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NOT NULL'))
    op.create_index('idx_ai_chat_sessions_user_id', 'ai_chat_sessions', ['user_id'])
    op.create_index('idx_ai_chat_sessions_deleted_at', 'ai_chat_sessions', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NOT NULL'))
    op.create_index('idx_ai_chat_messages_session_id', 'ai_chat_messages', ['session_id'])
    op.create_index('idx_ai_chat_messages_created_at', 'ai_chat_messages', ['created_at'], postgresql_where=sa.text('created_at DESC'))


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_ai_chat_messages_created_at', table_name='ai_chat_messages')
    op.drop_index('idx_ai_chat_messages_session_id', table_name='ai_chat_messages')
    op.drop_index('idx_ai_chat_sessions_deleted_at', table_name='ai_chat_sessions')
    op.drop_index('idx_ai_chat_sessions_user_id', table_name='ai_chat_sessions')
    op.drop_index('idx_ai_prompts_deleted_at', table_name='ai_prompts')
    op.drop_index('idx_ai_prompts_category', table_name='ai_prompts')
    op.drop_index('idx_ai_embeddings_resource_type_id', table_name='ai_embeddings')
    op.drop_index('idx_ai_analyses_created_at', table_name='ai_analyses')
    op.drop_index('idx_ai_analyses_status', table_name='ai_analyses')
    op.drop_index('idx_ai_analyses_resource_type_id', table_name='ai_analyses')
    op.drop_index('idx_ai_models_deleted_at', table_name='ai_models')
    op.drop_index('idx_ai_models_provider', table_name='ai_models')
    
    # Drop tables
    op.drop_table('ai_chat_messages')
    op.drop_table('ai_chat_sessions')
    op.drop_table('ai_prompts')
    op.drop_table('ai_embeddings')
    op.drop_table('ai_analyses')
    op.drop_table('ai_models')