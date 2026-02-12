"""Initial data pipeline service schema

Revision ID: 3c4d5e6f7a8b
Revises: 
Create Date: 2026-02-12 10:30:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3c4d5e6f7a8b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create data_sources table
    op.create_table('data_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=True),
        sa.Column('credentials', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create data_pipelines table
    op.create_table('data_pipelines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('destination_type', sa.String(length=50), nullable=False),
        sa.Column('destination_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('schedule', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='inactive'),
        sa.Column('last_run_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('next_run_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['source_id'], ['data_sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create pipeline_runs table
    op.create_table('pipeline_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pipeline_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('start_time', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('end_time', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True, default=0),
        sa.Column('records_failed', sa.Integer(), nullable=True, default=0),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['pipeline_id'], ['data_pipelines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create data_transformations table
    op.create_table('data_transformations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pipeline_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['pipeline_id'], ['data_pipelines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create data_validation_rules table
    op.create_table('data_validation_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pipeline_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_name', sa.String(length=255), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('rule_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False, default='warning'),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['pipeline_id'], ['data_pipelines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create scraped_data table
    op.create_table('scraped_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_url', sa.String(length=2048), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('html_content', sa.Text(), nullable=True),
        sa.Column('extracted_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_data_sources_type', 'data_sources', ['type'])
    op.create_index('idx_data_sources_deleted_at', 'data_sources', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NOT NULL'))
    op.create_index('idx_data_pipelines_source_id', 'data_pipelines', ['source_id'])
    op.create_index('idx_data_pipelines_status', 'data_pipelines', ['status'])
    op.create_index('idx_data_pipelines_next_run_at', 'data_pipelines', ['next_run_at'])
    op.create_index('idx_pipeline_runs_pipeline_id', 'pipeline_runs', ['pipeline_id'])
    op.create_index('idx_pipeline_runs_status', 'pipeline_runs', ['status'])
    op.create_index('idx_pipeline_runs_start_time', 'pipeline_runs', ['start_time'], postgresql_where=sa.text('start_time DESC'))
    op.create_index('idx_data_transformations_pipeline_id', 'data_transformations', ['pipeline_id'])
    op.create_index('idx_data_transformations_order', 'data_transformations', ['order'])
    op.create_index('idx_data_validation_rules_pipeline_id', 'data_validation_rules', ['pipeline_id'])
    op.create_index('idx_scraped_data_source_url', 'scraped_data', ['source_url'])
    op.create_index('idx_scraped_data_created_at', 'scraped_data', ['created_at'], postgresql_where=sa.text('created_at DESC'))


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_scraped_data_created_at', table_name='scraped_data')
    op.drop_index('idx_scraped_data_source_url', table_name='scraped_data')
    op.drop_index('idx_data_validation_rules_pipeline_id', table_name='data_validation_rules')
    op.drop_index('idx_data_transformations_order', table_name='data_transformations')
    op.drop_index('idx_data_transformations_pipeline_id', table_name='data_transformations')
    op.drop_index('idx_pipeline_runs_start_time', table_name='pipeline_runs')
    op.drop_index('idx_pipeline_runs_status', table_name='pipeline_runs')
    op.drop_index('idx_pipeline_runs_pipeline_id', table_name='pipeline_runs')
    op.drop_index('idx_data_pipelines_next_run_at', table_name='data_pipelines')
    op.drop_index('idx_data_pipelines_status', table_name='data_pipelines')
    op.drop_index('idx_data_pipelines_source_id', table_name='data_pipelines')
    op.drop_index('idx_data_sources_deleted_at', table_name='data_sources')
    op.drop_index('idx_data_sources_type', table_name='data_sources')
    
    # Drop tables
    op.drop_table('scraped_data')
    op.drop_table('data_validation_rules')
    op.drop_table('data_transformations')
    op.drop_table('pipeline_runs')
    op.drop_table('data_pipelines')
    op.drop_table('data_sources')