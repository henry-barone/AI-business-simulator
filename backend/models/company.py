from datetime import datetime
from . import db

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    webhook_triggered = db.Column(db.Boolean, default=False)
    
    pl_statements = db.relationship('PLStatement', backref='company', lazy=True, cascade='all, delete-orphan')
    questionnaire_responses = db.relationship('QuestionnaireResponse', backref='company', lazy=True, cascade='all, delete-orphan')
    simulations = db.relationship('Simulation', backref='company', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'industry': self.industry,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'webhook_triggered': self.webhook_triggered
        }