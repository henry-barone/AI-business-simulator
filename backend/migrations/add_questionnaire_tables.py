"""Add questionnaire tables for intelligent questionnaire system

Revision ID: add_questionnaire_tables
Revises: previous_migration
Create Date: 2025-07-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = 'add_questionnaire_tables'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None

def upgrade():
    # Create questionnaire_sessions table
    op.create_table('questionnaire_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('current_question', sa.String(50), nullable=False, default='START'),
        sa.Column('status', sa.String(20), nullable=False, default='in_progress'),
    )
    
    # Create questionnaire_responses table
    op.create_table('questionnaire_responses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('questionnaire_sessions.id'), nullable=False),
        sa.Column('question_id', sa.String(50), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('answer_type', sa.String(20), nullable=False),
        sa.Column('answered_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('ai_analyzed', sa.Boolean(), nullable=False, default=False),
        sa.Column('extracted_insights', sa.Text(), nullable=True),
    )
    
    # Create questionnaire_analysis table
    op.create_table('questionnaire_analysis',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('questionnaire_sessions.id'), nullable=False),
        sa.Column('company_type', sa.String(100), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('size_category', sa.String(50), nullable=True),
        sa.Column('production_volume', sa.String(50), nullable=True),
        sa.Column('pain_points', sa.Text(), nullable=True),
        sa.Column('opportunities', sa.Text(), nullable=True),
        sa.Column('automation_level', sa.String(50), nullable=True),
        sa.Column('priority_areas', sa.Text(), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('confidence_score', sa.Float(), nullable=True),
    )
    
    # Create indexes for better performance
    op.create_index('idx_questionnaire_responses_session_id', 'questionnaire_responses', ['session_id'])
    op.create_index('idx_questionnaire_responses_question_id', 'questionnaire_responses', ['question_id'])
    op.create_index('idx_questionnaire_analysis_session_id', 'questionnaire_analysis', ['session_id'])
    op.create_index('idx_questionnaire_sessions_status', 'questionnaire_sessions', ['status'])

def downgrade():
    # Drop indexes
    op.drop_index('idx_questionnaire_sessions_status', 'questionnaire_sessions')
    op.drop_index('idx_questionnaire_analysis_session_id', 'questionnaire_analysis')
    op.drop_index('idx_questionnaire_responses_question_id', 'questionnaire_responses')
    op.drop_index('idx_questionnaire_responses_session_id', 'questionnaire_responses')
    
    # Drop tables in reverse order (foreign keys first)
    op.drop_table('questionnaire_analysis')
    op.drop_table('questionnaire_responses')
    op.drop_table('questionnaire_sessions')