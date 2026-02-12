"""Initial reporting service schema

Revision ID: 5e6f7a8b9c0d
Revises: 
Create Date: 2026-02-12 11:00:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5e6f7a8b9c0d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create report_templates table
    op.create_table('report_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('template_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create reports table
    op.create_table('reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='queued'),
        sa.Column('output_url', sa.String(length=2048), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('generated_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('expires_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['template_id'], ['report_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create report_schedules table
    op.create_table('report_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('schedule_type', sa.String(length=50), nullable=False),
        sa.Column('cron_expression', sa.String(length=100), nullable=True),
        sa.Column('next_run_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('last_run_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['template_id'], ['report_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create report_metrics table
    op.create_table('report_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('measured_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create dashboards table
    op.create_table('dashboards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layout', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('widgets', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create dashboard_widgets table
    op.create_table('dashboard_widgets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('widget_type', sa.String(length=50), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('position_x', sa.Integer(), nullable=False),
        sa.Column('position_y', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_report_templates_type', 'report_templates', ['type'])
    op.create_index('idx_report_templates_deleted_at', 'report_templates', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NOT NULL'))
    op.create_index('idx_reports_template_id', 'reports', ['template_id'])
    op.create_index('idx_reports_user_id', 'reports', ['user_id'])
    op.create_index('idx_reports_status', 'reports', ['status'])
    op.create_index('idx_reports_created_at', 'reports', ['created_at'], postgresql_where=sa.text('created_at DESC'))
    op.create_index('idx_report_schedules_template_id', 'report_schedules', ['template_id'])
    op.create_index('idx_report_schedules_user_id', 'report_schedules', ['user_id'])
    op.create_index('idx_report_schedules_next_run_at', 'report_schedules', ['next_run_at'])
    op.create_index('idx_report_schedules_is_active', 'report_schedules', ['is_active'])
    op.create_index('idx_report_metrics_report_id', 'report_metrics', ['report_id'])
    op.create_index('idx_report_metrics_metric_name', 'report_metrics', ['metric_name'])
    op.create_index('idx_dashboards_deleted_at', 'dashboards', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NOT NULL'))
    op.create_index('idx_dashboard_widgets_dashboard_id', 'dashboard_widgets', ['dashboard_id'])
    op.create_index('idx_dashboard_widgets_position', 'dashboard_widgets', ['position_x', 'position_y'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_dashboard_widgets_position', table_name='dashboard_widgets')
    op.drop_index('idx_dashboard_widgets_dashboard_id', table_name='dashboard_widgets')
    op.drop_index('idx_dashboards_deleted_at', table_name='dashboards')
    op.drop_index('idx_report_metrics_metric_name', table_name='report_metrics')
    op.drop_index('idx_report_metrics_report_id', table_name='report_metrics')
    op.drop_index('idx_report_schedules_is_active', table_name='report_schedules')
    op.drop_index('idx_report_schedules_next_run_at', table_name='report_schedules')
    op.drop_index('idx_report_schedules_user_id', table_name='report_schedules')
    op.drop_index('idx_report_schedules_template_id', table_name='report_schedules')
    op.drop_index('idx_reports_created_at', table_name='reports')
    op.drop_index('idx_reports_status', table_name='reports')
    op.drop_index('idx_reports_user_id', table_name='reports')
    op.drop_index('idx_reports_template_id', table_name='reports')
    op.drop_index('idx_report_templates_deleted_at', table_name='report_templates')
    op.drop_index('idx_report_templates_type', table_name='report_templates')
    
    # Drop tables
    op.drop_table('dashboard_widgets')
    op.drop_table('dashboards')
    op.drop_table('report_metrics')
    op.drop_table('report_schedules')
    op.drop_table('reports')
    op.drop_table('report_templates')