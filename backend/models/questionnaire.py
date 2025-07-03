from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from typing import Dict, List, Any, Optional

db = SQLAlchemy()

class QuestionnaireSession(db.Model):
    __tablename__ = 'questionnaire_sessions'
    
    id = db.Column(db.String(36), primary_key=True)
    company_id = db.Column(db.String(36), nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    current_question = db.Column(db.String(50), default='START')
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, abandoned
    
    # Relationships
    responses = db.relationship('QuestionnaireResponse', backref='session', lazy=True, cascade='all, delete-orphan')
    analysis = db.relationship('QuestionnaireAnalysis', backref='session', uselist=False, cascade='all, delete-orphan')

class QuestionnaireResponse(db.Model):
    __tablename__ = 'questionnaire_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('questionnaire_sessions.id'), nullable=False)
    question_id = db.Column(db.String(50), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    answer_type = db.Column(db.String(20), nullable=False)  # select, text, number
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # For AI analysis of free text responses
    ai_analyzed = db.Column(db.Boolean, default=False)
    extracted_insights = db.Column(db.Text, nullable=True)  # JSON string

class QuestionnaireAnalysis(db.Model):
    __tablename__ = 'questionnaire_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('questionnaire_sessions.id'), nullable=False)
    
    # Company profile extracted from responses
    company_type = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    size_category = db.Column(db.String(50), nullable=True)
    production_volume = db.Column(db.String(50), nullable=True)
    
    # AI-extracted insights
    pain_points = db.Column(db.Text, nullable=True)  # JSON array
    opportunities = db.Column(db.Text, nullable=True)  # JSON array
    automation_level = db.Column(db.String(50), nullable=True)
    priority_areas = db.Column(db.Text, nullable=True)  # JSON array
    
    # Analysis metadata
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_score = db.Column(db.Float, nullable=True)
    
    def get_pain_points(self) -> List[str]:
        """Get pain points as a list."""
        return json.loads(self.pain_points) if self.pain_points else []
    
    def set_pain_points(self, points: List[str]):
        """Set pain points from a list."""
        self.pain_points = json.dumps(points)
    
    def get_opportunities(self) -> List[str]:
        """Get opportunities as a list."""
        return json.loads(self.opportunities) if self.opportunities else []
    
    def set_opportunities(self, opps: List[str]):
        """Set opportunities from a list."""
        self.opportunities = json.dumps(opps)
    
    def get_priority_areas(self) -> List[str]:
        """Get priority areas as a list."""
        return json.loads(self.priority_areas) if self.priority_areas else []
    
    def set_priority_areas(self, areas: List[str]):
        """Set priority areas from a list."""
        self.priority_areas = json.dumps(areas)