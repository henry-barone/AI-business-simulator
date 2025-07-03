from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from models import db
from models.company import Company
from models.simulation import Simulation, PLStatement, QuestionnaireResponse

simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/create', methods=['POST'])
def create_simulation():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        company_id = data.get('company_id')
        assumptions = data.get('assumptions', {})
        
        if not company_id:
            return jsonify({'error': 'Company ID required'}), 400
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get latest P&L data for baseline
        latest_pl = PLStatement.query.filter_by(company_id=company_id).order_by(PLStatement.uploaded_at.desc()).first()
        
        if not latest_pl:
            return jsonify({'error': 'No P&L data found for company'}), 400
        
        baseline_data = {
            'revenue': float(latest_pl.revenue) if latest_pl.revenue else 0,
            'cogs': float(latest_pl.cogs) if latest_pl.cogs else 0,
            'labor_costs': float(latest_pl.labor_costs) if latest_pl.labor_costs else 0,
            'overhead_costs': float(latest_pl.overhead_costs) if latest_pl.overhead_costs else 0,
            'other_costs': latest_pl.other_costs or {}
        }
        
        # Run simulation logic (placeholder)
        optimized_data = run_business_simulation(baseline_data, assumptions)
        
        simulation = Simulation(
            company_id=company_id,
            baseline_data=baseline_data,
            optimized_data=optimized_data,
            assumptions=assumptions
        )
        
        db.session.add(simulation)
        db.session.commit()
        
        current_app.logger.info(f"Simulation created for company {company_id}: {simulation.id}")
        
        return jsonify({
            'message': 'Simulation created successfully',
            'simulation_id': simulation.id,
            'baseline_data': baseline_data,
            'optimized_data': optimized_data,
            'assumptions': assumptions,
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Simulation creation error: {e}")
        return jsonify({'error': 'Simulation creation failed'}), 500

@simulation_bp.route('/<int:simulation_id>', methods=['GET'])
def get_simulation(simulation_id):
    try:
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return jsonify({'error': 'Simulation not found'}), 404
        
        return jsonify({
            'simulation': simulation.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get simulation error: {e}")
        return jsonify({'error': 'Failed to retrieve simulation'}), 500

@simulation_bp.route('/company/<int:company_id>', methods=['GET'])
def get_company_simulations(company_id):
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        simulations = Simulation.query.filter_by(company_id=company_id).order_by(Simulation.created_at.desc()).all()
        
        simulation_data = []
        for simulation in simulations:
            simulation_data.append(simulation.to_dict())
        
        return jsonify({
            'company_id': company_id,
            'simulations': simulation_data,
            'total_simulations': len(simulation_data),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get company simulations error: {e}")
        return jsonify({'error': 'Failed to retrieve simulations'}), 500

@simulation_bp.route('/run-sandbox', methods=['POST'])
def run_sandbox_simulation():
    try:
        data = request.get_json()
        
        if not data:
            # Default sandbox parameters
            price = 30.0
            ad_spend = 200.0
        else:
            price = float(data.get('price', 30.0))
            ad_spend = float(data.get('ad_spend', 200.0))
        
        # Import and run legacy simulation engine
        try:
            from services.simulation_engine import BusinessModel
            
            business_model = BusinessModel()
            results = business_model.run_simulation(price, ad_spend)
            
            return jsonify({
                'results': results,
                'parameters': {
                    'price': price,
                    'ad_spend': ad_spend
                },
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except ImportError:
            # Fallback simulation if engine not available
            results = generate_mock_simulation_results(price, ad_spend)
            
            return jsonify({
                'results': results,
                'parameters': {
                    'price': price,
                    'ad_spend': ad_spend
                },
                'mock': True,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        
    except ValueError as e:
        current_app.logger.error(f"Invalid parameters in sandbox simulation: {e}")
        return jsonify({'error': 'Invalid parameters'}), 400
    except Exception as e:
        current_app.logger.error(f"Sandbox simulation error: {e}")
        return jsonify({'error': 'Simulation failed'}), 500

def run_business_simulation(baseline_data, assumptions):
    # Placeholder simulation logic
    # In production, implement sophisticated business simulation algorithms
    
    optimized_data = baseline_data.copy()
    
    # Apply optimization assumptions
    if 'revenue_growth' in assumptions:
        optimized_data['revenue'] *= (1 + assumptions['revenue_growth'] / 100)
    
    if 'cost_reduction' in assumptions:
        optimized_data['cogs'] *= (1 - assumptions['cost_reduction'] / 100)
        optimized_data['overhead_costs'] *= (1 - assumptions['cost_reduction'] / 100)
    
    # Calculate profit metrics
    baseline_profit = baseline_data['revenue'] - baseline_data['cogs'] - baseline_data['labor_costs'] - baseline_data['overhead_costs']
    optimized_profit = optimized_data['revenue'] - optimized_data['cogs'] - optimized_data['labor_costs'] - optimized_data['overhead_costs']
    
    optimized_data['profit_improvement'] = optimized_profit - baseline_profit
    optimized_data['profit_improvement_percent'] = ((optimized_profit - baseline_profit) / baseline_profit * 100) if baseline_profit != 0 else 0
    
    return optimized_data

def generate_mock_simulation_results(price, ad_spend):
    # Generate mock monthly results for 12 months
    import random
    
    base_units = max(1, int(ad_spend / 10))  # Simple relationship between ad spend and units sold
    base_profit = price * base_units * 0.3  # Assume 30% profit margin
    
    monthly_results = []
    for month in range(12):
        # Add some variability
        units_variation = random.uniform(0.8, 1.2)
        units_sold = int(base_units * units_variation)
        monthly_profit = price * units_sold * 0.3
        
        monthly_results.append(round(monthly_profit, 2))
    
    return monthly_results