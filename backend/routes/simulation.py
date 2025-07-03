from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from datetime import datetime
import logging
from typing import Dict, Any

from models import db
from models.company import Company
from models.simulation import Simulation, PLStatement, QuestionnaireResponse
from models.questionnaire import QuestionnaireSession, QuestionnaireResponse as QResponse, QuestionnaireAnalysis
from services.simulation_engine import SimulationEngine
from services.pl_analyzer import PLAnalyzer
from services.ai_service import AIService

logger = logging.getLogger(__name__)

simulation_bp = Blueprint('simulation', __name__)
simulation_engine = SimulationEngine()
pl_analyzer = PLAnalyzer()
ai_service = AIService()

@simulation_bp.route('/api/companies/<int:company_id>/simulation', methods=['GET'])
@cross_origin()
def get_company_simulation(company_id):
    """Retrieve existing simulation for a company."""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'success': False, 'error': 'Company not found'}), 404
        
        # Get latest simulation
        simulation = Simulation.query.filter_by(company_id=company_id).order_by(Simulation.created_at.desc()).first()
        
        if not simulation:
            return jsonify({
                'success': False,
                'error': 'No simulation found for company',
                'company_id': company_id
            }), 404
        
        return jsonify({
            'success': True,
            'simulation': simulation.to_dict(),
            'company_id': company_id
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get company simulation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@simulation_bp.route('/api/companies/<int:company_id>/simulate', methods=['POST'])
@cross_origin()
def create_company_simulation(company_id):
    """Create new simulation using PLAnalyzer data + questionnaire responses + AI recommendations."""
    try:
        data = request.get_json() or {}
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'success': False, 'error': 'Company not found'}), 404
        
        # Get P&L data
        pl_file_path = data.get('pl_file_path')
        if pl_file_path:
            # Parse P&L file
            pl_data = pl_analyzer.parse_file(pl_file_path)
            if pl_data.get('error'):
                return jsonify({'success': False, 'error': f"P&L parsing failed: {pl_data['error']}"}), 400
            
            financial_data = {
                'revenue': pl_data.get('revenue', 0),
                'cogs': pl_data.get('cogs', 0),
                'labor_costs': pl_data.get('labor_costs', 0),
                'overhead_costs': pl_data.get('overhead_costs', 0)
            }
        else:
            # Get latest P&L from database
            latest_pl = PLStatement.query.filter_by(company_id=company_id).order_by(PLStatement.uploaded_at.desc()).first()
            if not latest_pl:
                return jsonify({'success': False, 'error': 'No P&L data found for company'}), 400
            
            financial_data = {
                'revenue': float(latest_pl.revenue) if latest_pl.revenue else 0,
                'cogs': float(latest_pl.cogs) if latest_pl.cogs else 0,
                'labor_costs': float(latest_pl.labor_costs) if latest_pl.labor_costs else 0,
                'overhead_costs': float(latest_pl.overhead_costs) if latest_pl.overhead_costs else 0
            }
        
        # Get questionnaire data
        session_id = data.get('session_id')
        if session_id:
            session = QuestionnaireSession.query.filter_by(id=session_id).first()
            if not session:
                return jsonify({'success': False, 'error': 'Questionnaire session not found'}), 404
            
            responses = QResponse.query.filter_by(session_id=session_id).all()
            
            # Build company profile from questionnaire
            company_profile = {'industry': 'Manufacturing'}
            questionnaire_responses = []
            
            for resp in responses:
                response_dict = {
                    'question_id': resp.question_id,
                    'question_text': resp.question_text,
                    'answer': resp.answer,
                    'answer_type': resp.answer_type
                }
                questionnaire_responses.append(response_dict)
                
                # Extract key profile data
                if resp.question_id == 'START':
                    company_profile['product_type'] = resp.answer
                elif resp.question_id in ['VOLUME', 'GENERAL_1']:
                    company_profile['production_volume'] = resp.answer
                elif resp.question_id == 'EMPLOYEES':
                    company_profile['employee_count'] = resp.answer
                elif resp.question_id == 'AUTOMATION_CURRENT':
                    company_profile['automation_level'] = resp.answer
        else:
            # Default company profile
            company_profile = {
                'industry': 'Manufacturing',
                'product_type': 'Unknown',
                'employee_count': '11-50 employees',
                'production_volume': '1000-10000 units/day',
                'automation_level': 'Some automated tools'
            }
            questionnaire_responses = []
        
        # Combine data for baseline creation
        company_data = {
            'financial_data': financial_data,
            'company_profile': company_profile,
            'questionnaire_responses': questionnaire_responses
        }
        
        # Create baseline model
        baseline = simulation_engine.create_baseline(company_data)
        
        # Generate AI recommendations
        ai_analysis = ai_service.analyze_comprehensive(
            {'company_profile': company_profile, 'responses': questionnaire_responses},
            financial_data
        )
        
        # Convert AI recommendations to Recommendation objects
        from services.ai_service import Recommendation
        recommendations = []
        for rec_data in ai_analysis.get('recommendations', []):
            rec_info = rec_data['recommendation']
            recommendation = Recommendation(
                title=rec_info['title'],
                description=rec_info['description'],
                category=rec_info['category'],
                priority=rec_info['priority'],
                implementation_effort=rec_info['implementation_effort'],
                technology_type=rec_info['technology_type'],
                target_pain_points=rec_info['target_pain_points'],
                estimated_timeline=rec_info['estimated_timeline'],
                confidence=rec_info['confidence']
            )
            recommendations.append(recommendation)
        
        # Apply optimizations
        optimization_scenarios = simulation_engine.apply_optimizations(baseline, recommendations)
        
        # Generate projections for best scenario
        best_scenario = optimization_scenarios[0] if optimization_scenarios else None
        projections = {}
        roi_metrics = {}
        
        if best_scenario:
            projections = simulation_engine.project_timeline(best_scenario, 12)
            roi_metrics = simulation_engine.calculate_roi(baseline, best_scenario, 12)
        
        # Create simulation record
        simulation_data = {
            'baseline': {
                'revenue': baseline.revenue,
                'cogs': baseline.cogs,
                'labor_costs': baseline.labor_costs,
                'overhead_costs': baseline.overhead_costs,
                'monthly_profit': baseline.monthly_profit,
                'employee_count': baseline.employee_count,
                'production_volume': baseline.production_volume,
                'automation_level': baseline.automation_level
            },
            'optimization_scenarios': [
                {
                    'name': scenario.name,
                    'implementation_costs': scenario.implementation_costs,
                    'implementation_months': scenario.implementation_months
                } for scenario in optimization_scenarios
            ],
            'projections': {
                period: {
                    'months': proj.months,
                    'cumulative_savings': proj.cumulative_savings,
                    'cumulative_costs': proj.cumulative_costs,
                    'net_benefit': proj.net_benefit,
                    'roi_percentage': proj.roi_percentage,
                    'payback_achieved': proj.payback_achieved,
                    'break_even_month': proj.break_even_month,
                    'monthly_cash_flow': proj.monthly_cash_flow,
                    'cumulative_cash_flow': proj.cumulative_cash_flow
                } for period, proj in projections.items()
            },
            'roi_metrics': roi_metrics,
            'ai_analysis': ai_analysis
        }
        
        # Save to database
        simulation = Simulation(
            company_id=company_id,
            baseline_data=simulation_data['baseline'],
            optimized_data=simulation_data,
            assumptions=data.get('assumptions', {})
        )
        
        db.session.add(simulation)
        db.session.commit()
        
        logger.info(f"Simulation created for company {company_id}: {simulation.id}")
        
        return jsonify({
            'success': True,
            'simulation_id': simulation.id,
            'simulation_data': simulation_data,
            'baseline': simulation_data['baseline'],
            'projections': simulation_data['projections'],
            'roi_metrics': roi_metrics,
            'recommendations_count': len(recommendations)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Simulation creation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@simulation_bp.route('/api/simulations/<int:simulation_id>/adjust', methods=['POST'])
@cross_origin()
def adjust_simulation(simulation_id):
    """Handle real-time slider adjustments."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No adjustment data provided'}), 400
        
        # Get simulation
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return jsonify({'success': False, 'error': 'Simulation not found'}), 404
        
        # Extract baseline data
        baseline_data = simulation.baseline_data
        
        # Create BaselineModel from stored data
        from services.simulation_engine import BaselineModel
        baseline = BaselineModel(
            revenue=baseline_data['revenue'],
            cogs=baseline_data['cogs'],
            labor_costs=baseline_data['labor_costs'],
            overhead_costs=baseline_data['overhead_costs'],
            production_volume=baseline_data.get('production_volume', 500000),
            employee_count=baseline_data.get('employee_count', 25),
            automation_level=baseline_data.get('automation_level', 'Some automated tools'),
            quality_defect_rate=0.05,
            labor_efficiency=1.0,
            inventory_turnover=4.0,
            equipment_uptime=0.85
        )
        
        # Extract adjustment parameters
        adjustments = {
            'labor_automation': data.get('labor_automation', 0),
            'quality_automation': data.get('quality_automation', 0),
            'inventory_automation': data.get('inventory_automation', 0),
            'timeline_months': data.get('timeline_months', 6)
        }
        
        # Validate adjustment parameters
        for key in ['labor_automation', 'quality_automation', 'inventory_automation']:
            value = adjustments[key]
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                return jsonify({'success': False, 'error': f'Invalid {key}: must be between 0-100'}), 400
        
        timeline_months = adjustments['timeline_months']
        if not isinstance(timeline_months, int) or timeline_months < 3 or timeline_months > 12:
            return jsonify({'success': False, 'error': 'Invalid timeline_months: must be between 3-12'}), 400
        
        # Calculate real-time adjustments
        adjustment_results = simulation_engine.adjust_real_time(baseline, adjustments)
        
        if not adjustment_results.get('success'):
            return jsonify({
                'success': False,
                'error': adjustment_results.get('error', 'Adjustment calculation failed')
            }), 500
        
        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'adjustments': adjustments,
            'results': adjustment_results
        }), 200
        
    except Exception as e:
        logger.error(f"Simulation adjustment failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@simulation_bp.route('/api/simulations/<int:simulation_id>', methods=['GET'])
@cross_origin()
def get_simulation(simulation_id):
    """Get detailed simulation data."""
    try:
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return jsonify({'success': False, 'error': 'Simulation not found'}), 404
        
        return jsonify({
            'success': True,
            'simulation': simulation.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get simulation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@simulation_bp.route('/api/companies/<int:company_id>/simulations', methods=['GET'])
@cross_origin()
def get_company_simulations(company_id):
    """Get all simulations for a company."""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'success': False, 'error': 'Company not found'}), 404
        
        simulations = Simulation.query.filter_by(company_id=company_id).order_by(Simulation.created_at.desc()).all()
        
        simulation_data = []
        for simulation in simulations:
            simulation_data.append(simulation.to_dict())
        
        return jsonify({
            'success': True,
            'company_id': company_id,
            'simulations': simulation_data,
            'total_simulations': len(simulation_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get company simulations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Legacy sandbox route for backward compatibility
@simulation_bp.route('/run-sandbox', methods=['POST'])
@cross_origin()
def run_sandbox_simulation():
    """Legacy sandbox simulation endpoint."""
    try:
        data = request.get_json() or {}
        
        price = float(data.get('price', 30.0))
        ad_spend = float(data.get('ad_spend', 200.0))
        
        # Generate simple mock results
        results = generate_mock_simulation_results(price, ad_spend)
        
        return jsonify({
            'success': True,
            'results': results,
            'parameters': {
                'price': price,
                'ad_spend': ad_spend
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid parameters in sandbox simulation: {e}")
        return jsonify({'success': False, 'error': 'Invalid parameters'}), 400
    except Exception as e:
        logger.error(f"Sandbox simulation error: {e}")
        return jsonify({'success': False, 'error': 'Simulation failed'}), 500

def generate_mock_simulation_results(price, ad_spend):
    """Generate mock monthly results for legacy compatibility."""
    import random
    
    base_units = max(1, int(ad_spend / 10))
    base_profit = price * base_units * 0.3
    
    monthly_results = []
    for month in range(12):
        units_variation = random.uniform(0.8, 1.2)
        units_sold = int(base_units * units_variation)
        monthly_profit = price * units_sold * 0.3
        monthly_results.append(round(monthly_profit, 2))
    
    return monthly_results