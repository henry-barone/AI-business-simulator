from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from . import db

class PLStatement(db.Model):
    __tablename__ = 'pl_statements'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    revenue = db.Column(db.Numeric(12, 2))
    cogs = db.Column(db.Numeric(12, 2))
    labor_costs = db.Column(db.Numeric(12, 2))
    overhead_costs = db.Column(db.Numeric(12, 2))
    other_costs = db.Column(JSONB)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PLStatement Company:{self.company_id} Revenue:{self.revenue}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'revenue': float(self.revenue) if self.revenue else None,
            'cogs': float(self.cogs) if self.cogs else None,
            'labor_costs': float(self.labor_costs) if self.labor_costs else None,
            'overhead_costs': float(self.overhead_costs) if self.overhead_costs else None,
            'other_costs': self.other_costs,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

class QuestionnaireResponse(db.Model):
    __tablename__ = 'questionnaire_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    question_id = db.Column(db.String(50), nullable=False)
    answer = db.Column(db.Text)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QuestionnaireResponse Company:{self.company_id} Question:{self.question_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'question_id': self.question_id,
            'answer': self.answer,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None
        }

class Simulation(db.Model):
    __tablename__ = 'simulations'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    baseline_data = db.Column(JSONB)
    optimized_data = db.Column(JSONB)
    assumptions = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    recommendations = db.relationship('Recommendation', backref='simulation', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Simulation Company:{self.company_id} ID:{self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'baseline_data': self.baseline_data,
            'optimized_data': self.optimized_data,
            'assumptions': self.assumptions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }