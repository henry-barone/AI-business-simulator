from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from models import db
from models.simulation import Simulation
from models.recommendation import Recommendation

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/generate/<int:simulation_id>', methods=['POST'])
def generate_recommendations(simulation_id):
    try:
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return jsonify({'error': 'Simulation not found'}), 404
        
        # Clear existing recommendations for this simulation
        Recommendation.query.filter_by(simulation_id=simulation_id).delete()
        
        # Generate new recommendations based on simulation data
        recommendations = generate_business_recommendations(simulation)
        
        saved_recommendations = []
        for rec_data in recommendations:
            recommendation = Recommendation(
                simulation_id=simulation_id,
                recommendation_type=rec_data['type'],
                description=rec_data['description'],
                estimated_savings=rec_data.get('estimated_savings'),
                implementation_cost=rec_data.get('implementation_cost'),
                priority=rec_data.get('priority', 3)
            )
            db.session.add(recommendation)
            saved_recommendations.append(recommendation)
        
        db.session.commit()
        
        current_app.logger.info(f"Generated {len(saved_recommendations)} recommendations for simulation {simulation_id}")
        
        return jsonify({
            'message': 'Recommendations generated successfully',
            'simulation_id': simulation_id,
            'recommendations_count': len(saved_recommendations),
            'recommendations': [rec.to_dict() for rec in saved_recommendations],
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Recommendation generation error: {e}")
        return jsonify({'error': 'Failed to generate recommendations'}), 500

@recommendations_bp.route('/simulation/<int:simulation_id>', methods=['GET'])
def get_simulation_recommendations(simulation_id):
    try:
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return jsonify({'error': 'Simulation not found'}), 404
        
        recommendations = Recommendation.query.filter_by(simulation_id=simulation_id).order_by(Recommendation.priority.asc()).all()
        
        recommendation_data = []
        for recommendation in recommendations:
            recommendation_data.append(recommendation.to_dict())
        
        return jsonify({
            'simulation_id': simulation_id,
            'recommendations': recommendation_data,
            'total_recommendations': len(recommendation_data),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get recommendations error: {e}")
        return jsonify({'error': 'Failed to retrieve recommendations'}), 500

@recommendations_bp.route('/<int:recommendation_id>', methods=['GET'])
def get_recommendation(recommendation_id):
    try:
        recommendation = Recommendation.query.get(recommendation_id)
        if not recommendation:
            return jsonify({'error': 'Recommendation not found'}), 404
        
        return jsonify({
            'recommendation': recommendation.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get recommendation error: {e}")
        return jsonify({'error': 'Failed to retrieve recommendation'}), 500

@recommendations_bp.route('/<int:recommendation_id>', methods=['PUT'])
def update_recommendation(recommendation_id):
    try:
        recommendation = Recommendation.query.get(recommendation_id)
        if not recommendation:
            return jsonify({'error': 'Recommendation not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update recommendation fields
        if 'description' in data:
            recommendation.description = data['description']
        if 'estimated_savings' in data:
            recommendation.estimated_savings = data['estimated_savings']
        if 'implementation_cost' in data:
            recommendation.implementation_cost = data['implementation_cost']
        if 'priority' in data:
            recommendation.priority = data['priority']
        
        db.session.commit()
        
        current_app.logger.info(f"Updated recommendation {recommendation_id}")
        
        return jsonify({
            'message': 'Recommendation updated successfully',
            'recommendation': recommendation.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update recommendation error: {e}")
        return jsonify({'error': 'Failed to update recommendation'}), 500

def generate_business_recommendations(simulation):
    """
    Generate business recommendations based on simulation data.
    This is a placeholder implementation - customize based on your business logic.
    """
    baseline = simulation.baseline_data
    optimized = simulation.optimized_data
    
    recommendations = []
    
    # Revenue optimization recommendations
    if baseline.get('revenue', 0) > 0:
        revenue_improvement = optimized.get('revenue', 0) - baseline.get('revenue', 0)
        if revenue_improvement > 0:
            recommendations.append({
                'type': 'Revenue Optimization',
                'description': f'Implement strategies to increase revenue by ${revenue_improvement:,.2f}. Focus on customer acquisition, pricing optimization, and market expansion.',
                'estimated_savings': revenue_improvement,
                'implementation_cost': revenue_improvement * 0.2,  # 20% of potential gain
                'priority': 1
            })
    
    # Cost reduction recommendations
    baseline_costs = baseline.get('cogs', 0) + baseline.get('overhead_costs', 0)
    optimized_costs = optimized.get('cogs', 0) + optimized.get('overhead_costs', 0)
    cost_savings = baseline_costs - optimized_costs
    
    if cost_savings > 0:
        recommendations.append({
            'type': 'Cost Reduction',
            'description': f'Optimize operational costs to save ${cost_savings:,.2f}. Consider supplier negotiations, process automation, and overhead reduction.',
            'estimated_savings': cost_savings,
            'implementation_cost': cost_savings * 0.1,  # 10% of savings
            'priority': 2
        })
    
    # Labor efficiency recommendations
    labor_costs = baseline.get('labor_costs', 0)
    if labor_costs > baseline.get('revenue', 1) * 0.3:  # If labor costs > 30% of revenue
        recommendations.append({
            'type': 'Labor Efficiency',
            'description': 'Labor costs are high relative to revenue. Consider productivity improvements, training programs, or workforce optimization.',
            'estimated_savings': labor_costs * 0.15,  # 15% potential savings
            'implementation_cost': labor_costs * 0.05,  # 5% investment
            'priority': 2
        })
    
    # Technology investment recommendations
    if baseline.get('revenue', 0) > 100000:  # For larger businesses
        recommendations.append({
            'type': 'Technology Investment',
            'description': 'Invest in technology solutions to improve efficiency, customer experience, and data analytics capabilities.',
            'estimated_savings': baseline.get('revenue', 0) * 0.05,  # 5% revenue improvement
            'implementation_cost': 25000,  # Fixed implementation cost
            'priority': 3
        })
    
    # Market expansion recommendations
    recommendations.append({
        'type': 'Market Expansion',
        'description': 'Explore new market segments or geographical expansion to drive growth. Consider digital marketing and partnerships.',
        'estimated_savings': baseline.get('revenue', 0) * 0.2,  # 20% revenue growth potential
        'implementation_cost': baseline.get('revenue', 0) * 0.1,  # 10% investment
        'priority': 3
    })
    
    return recommendations