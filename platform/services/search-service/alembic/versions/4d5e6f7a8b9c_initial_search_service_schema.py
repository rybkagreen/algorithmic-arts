"""Initial search service schema

Revision ID: 4d5e6f7a8b9c
Revises: 
Create Date: 2026-02-12 10:45:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4d5e6f7a8b9c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create search_indexes table
    op.create_table('search_indexes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='active'),
        sa.Column('mapping', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('total_documents', sa.Integer(), nullable=True, default=0),
        sa.Column('last_updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create search_queries table
    op.create_table('search_queries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('index_name', sa.String(length=255), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('query_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('results_count', sa.Integer(), nullable=True, default=0),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True, default=0),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create search_suggestions table
    op.create_table('search_suggestions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('index_name', sa.String(length=255), nullable=False),
        sa.Column('term', sa.String(length=255), nullable=False),
        sa.Column('document_count', sa.Integer(), nullable=True, default=0),
        sa.Column('score', sa.Numeric(precision=5, scale=3), nullable=True, default=1.0),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create search_relevance_feedback table
    op.create_table('search_relevance_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('query_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('relevance_score', sa.SmallInteger(), nullable=False),
        sa.Column('feedback_type', sa.String(length=20), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['query_id'], ['search_queries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create search_facets table
    op.create_table('search_facets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('index_name', sa.String(length=255), nullable=False),
        sa.Column('facet_name', sa.String(length=100), nullable=False),
        sa.Column('facet_type', sa.String(length=50), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_search_indexes_document_type', 'search_indexes', ['document_type'])
    op.create_index('idx_search_indexes_status', 'search_indexes', ['status'])
    op.create_index('idx_search_queries_user_id', 'search_queries', ['user_id'])
    op.create_index('idx_search_queries_index_name', 'search_queries', ['index_name'])
    op.create_index('idx_search_queries_created_at', 'search_queries', ['created_at'], postgresql_where=sa.text('created_at DESC'))
    op.create_index('idx_search_suggestions_index_name_term', 'search_suggestions', ['index_name', 'term'])
    op.create_index('idx_search_suggestions_score', 'search_suggestions', ['score'], postgresql_where=sa.text('score DESC'))
    op.create_index('idx_search_relevance_feedback_query_id', 'search_relevance_feedback', ['query_id'])
    op.create_index('idx_search_relevance_feedback_document_id', 'search_relevance_feedback', ['document_id'])
    op.create_index('idx_search_facets_index_name', 'search_facets', ['index_name'])
    op.create_index('idx_search_facets_facet_name', 'search_facets', ['facet_name'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_search_facets_facet_name', table_name='search_facets')
    op.drop_index('idx_search_facets_index_name', table_name='search_facets')
    op.drop_index('idx_search_relevance_feedback_document_id', table_name='search_relevance_feedback')
    op.drop_index('idx_search_relevance_feedback_query_id', table_name='search_relevance_feedback')
    op.drop_index('idx_search_suggestions_score', table_name='search_suggestions')
    op.drop_index('idx_search_suggestions_index_name_term', table_name='search_suggestions')
    op.drop_index('idx_search_queries_created_at', table_name='search_queries')
    op.drop_index('idx_search_queries_index_name', table_name='search_queries')
    op.drop_index('idx_search_queries_user_id', table_name='search_queries')
    op.drop_index('idx_search_indexes_status', table_name='search_indexes')
    op.drop_index('idx_search_indexes_document_type', table_name='search_indexes')
    
    # Drop tables
    op.drop_table('search_facets')
    op.drop_table('search_relevance_feedback')
    op.drop_table('search_suggestions')
    op.drop_table('search_queries')
    op.drop_table('search_indexes')