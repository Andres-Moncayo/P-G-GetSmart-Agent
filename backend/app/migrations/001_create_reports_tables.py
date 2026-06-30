"""
Database migration for Phase 4: Create reports and pipeline status tables.

This migration creates the necessary tables for storing analysis reports,
pipeline status tracking, and raw data storage.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create the reports-related tables."""
    
    # Create analysis_reports table
    op.create_table(
        'analysis_reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('quality_rating', sa.String(10), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('data_completeness', sa.Float(), nullable=False),
        sa.Column('game_id', sa.String(100), nullable=False),
        sa.Column('game_title', sa.String(500), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('title', sa.String(1000), nullable=False),
        sa.Column('markdown_content', sa.Text(), nullable=False),
        sa.Column('json_content', sa.JSON(), nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('language', sa.String(10), nullable=False),
        sa.Column('phases_completed', sa.JSON()),
        sa.Column('total_phases', sa.Integer(), nullable=False),
        sa.Column('processing_time_ms', sa.Integer()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for analysis_reports
    op.create_index(op.f('ix_analysis_reports_game_id'), 'analysis_reports', ['game_id'])
    op.create_index(op.f('ix_analysis_reports_status'), 'analysis_reports', ['status'])
    op.create_index(op.f('ix_analysis_reports_created_at'), 'analysis_reports', ['created_at'])
    op.create_index('ix_analysis_reports_game_title', 'analysis_reports', ['game_title'])
    
    # Create pipeline_status table
    op.create_table(
        'pipeline_status',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('report_id', sa.String(), nullable=False),
        sa.Column('phase_name', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('error_message', sa.Text()),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('phase_data', sa.JSON()),
        sa.ForeignKeyConstraint(['report_id'], ['analysis_reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for pipeline_status
    op.create_index(op.f('ix_pipeline_status_report_id'), 'pipeline_status', ['report_id'])
    op.create_index(op.f('ix_pipeline_status_phase_name'), 'pipeline_status', ['phase_name'])
    op.create_index('ix_pipeline_status_phase_report', 'pipeline_status', ['report_id', 'phase_name'])
    
    # Create raw_analysis_data table
    op.create_table(
        'raw_analysis_data',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('game_id', sa.String(100), nullable=False),
        sa.Column('phase', sa.String(50), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('data_type', sa.String(50), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON()),
        sa.Column('is_valid', sa.Boolean(), nullable=False),
        sa.Column('validation_errors', sa.JSON()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for raw_analysis_data
    op.create_index(op.f('ix_raw_analysis_data_game_id'), 'raw_analysis_data', ['game_id'])
    op.create_index(op.f('ix_raw_analysis_data_phase'), 'raw_analysis_data', ['phase'])
    op.create_index('ix_raw_data_game_phase', 'raw_analysis_data', ['game_id', 'phase'])
    op.create_index('ix_raw_data_is_valid', 'raw_analysis_data', ['is_valid'])


def downgrade():
    """Drop the reports-related tables."""
    
    # Drop tables in reverse order of creation
    op.drop_table('raw_analysis_data')
    op.drop_table('pipeline_status')
    op.drop_table('analysis_reports')
