from . import db

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    recommendation_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    estimated_savings = db.Column(db.Numeric(12, 2))
    implementation_cost = db.Column(db.Numeric(12, 2))
    priority = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<Recommendation Simulation:{self.simulation_id} Type:{self.recommendation_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'simulation_id': self.simulation_id,
            'recommendation_type': self.recommendation_type,
            'description': self.description,
            'estimated_savings': float(self.estimated_savings) if self.estimated_savings else None,
            'implementation_cost': float(self.implementation_cost) if self.implementation_cost else None,
            'priority': self.priority
        }