from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from datetime import datetime
import logging
from typing import Dict, Any

from models import db
from models.company import Company
from models.simulation import Simulation, PLStatement
from services.enhanced_simulation_engine import EnhancedSimulationEngine

logger = logging.getLogger(__name__)

enhanced_simulation_bp = Blueprint('enhanced_simulation', __name__)
enhanced_engine = EnhancedSimulationEngine()

@enhanced_simulation_bp.route('/api/companies/<int:company_id>/enhanced-simulation', methods=['POST'])
@cross_origin()
def create_enhanced_simulation(company_id):
    """Create enhanced simulation with manufacturing-specific calculations."""
    try:
        data = request.get_json() or {}
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'success': False, 'error': 'Company not found'}), 404
        
        # Get latest P&L data
        latest_pl = PLStatement.query.filter_by(company_id=company_id).order_by(PLStatement.uploaded_at.desc()).first()
        if not latest_pl:
            return jsonify({'success': False, 'error': 'No P&L data found for company'}), 400
        
        # Build company data for enhanced simulation
        company_data = {
            'financial_data': {
                'revenue': float(latest_pl.revenue) if latest_pl.revenue else 0,
                'cogs': float(latest_pl.cogs) if latest_pl.cogs else 0,
                'labor_costs': float(latest_pl.labor_costs) if latest_pl.labor_costs else 0,
                'overhead_costs': float(latest_pl.overhead_costs) if latest_pl.overhead_costs else 0
            },
            'company_profile': {
                'industry': company.industry,
                'production_volume': data.get('production_volume', '1000-10000 units/day'),
                'employee_count': data.get('employee_count', '51-200'),
                'automation_level': data.get('automation_level', 'Some automated tools')
            }
        }
        
        # Get questionnaire analysis for enhanced accuracy
        questionnaire_analysis = None
        try:
            from models.questionnaire import QuestionnaireSession, QuestionnaireAnalysis
            
            # Find the latest completed questionnaire session for this company
            latest_session = QuestionnaireSession.query.filter_by(
                company_id=company_id, 
                status='completed'
            ).order_by(QuestionnaireSession.completed_at.desc()).first()
            
            if latest_session:
                analysis = QuestionnaireAnalysis.query.filter_by(
                    session_id=latest_session.id
                ).first()
                
                if analysis:
                    questionnaire_analysis = {
                        'company_profile': {
                            'company_type': analysis.company_type,
                            'industry_category': analysis.industry,
                            'size_category': analysis.size_category,
                            'current_maturity': 'Basic'
                        },
                        'operational_assessment': {
                            'automation_percentage': '25%',
                            'quality_loss_percentage': '15%',
                            'production_volume_annual': '250,000 units/year'
                        },
                        'automation_opportunities': {
                            'labor_optimization': {'potential': 'medium'},
                            'quality_control': {'potential': 'medium'},
                            'inventory_management': {'potential': 'medium'},
                            'customer_service': {'potential': 'low'}
                        }
                    }
                    
                    logger.info(f"Using questionnaire analysis for enhanced simulation accuracy")
        except Exception as e:
            logger.warning(f"Could not load questionnaire analysis: {e}")
        
        # Create enhanced baseline with questionnaire insights
        baseline = enhanced_engine.create_enhanced_baseline(company_data, questionnaire_analysis)
        
        # Get automation levels from request
        automation_levels = data.get('automation_levels', {
            'labor': 0.5,
            'quality': 0.5,
            'inventory': 0.5,
            'service': 0.5
        })
        
        # Calculate detailed optimizations
        labor_opt = enhanced_engine.calculate_labor_optimization(baseline, automation_levels.get('labor', 0.5))
        quality_opt = enhanced_engine.calculate_quality_optimization(baseline, automation_levels.get('quality', 0.5))
        inventory_opt = enhanced_engine.calculate_inventory_optimization(baseline, automation_levels.get('inventory', 0.5))
        service_opt = enhanced_engine.calculate_service_automation(baseline, automation_levels.get('service', 0.5))
        
        # Generate monthly projections
        months = data.get('projection_months', 24)
        projections = enhanced_engine.generate_monthly_projections(baseline, automation_levels, months)
        
        # Analyze break-even
        break_even = enhanced_engine.analyze_break_even(projections)
        
        # Prepare response data with proper structure for frontend
        total_annual_savings = sum([
            labor_opt['total_annual_savings'],
            quality_opt['total_annual_savings'],
            inventory_opt['total_annual_savings'],
            service_opt['total_annual_savings']
        ])
        
        total_implementation_cost = sum([
            labor_opt['implementation_cost'] + labor_opt['training_cost'],
            quality_opt['quality_system_cost'] + quality_opt['training_cost'],
            inventory_opt['system_cost'] + inventory_opt['training_cost'],
            service_opt['automation_platform_cost'] + service_opt['setup_cost']
        ])
        
        simulation_data = {
            'baseline': {
                'revenue': baseline.revenue,
                'cogs': baseline.cogs,
                'labor_costs': baseline.labor_costs,
                'overhead_costs': baseline.overhead_costs,
                'production_volume': baseline.production_volume,
                'employee_count': baseline.employee_count,
                'cost_breakdown': {
                    'direct_labor_cost': baseline.cost_breakdown.direct_labor_cost,
                    'indirect_labor_cost': baseline.cost_breakdown.indirect_labor_cost,
                    'rework_cost': baseline.cost_breakdown.rework_cost,
                    'scrap_cost': baseline.cost_breakdown.scrap_cost,
                    'carrying_cost': baseline.cost_breakdown.carrying_cost,
                    'agent_salaries': baseline.cost_breakdown.agent_salaries,
                    'total_costs': baseline.cost_breakdown.total_costs()
                }
            },
            'optimizations': {
                'labor': labor_opt,
                'quality': quality_opt,
                'inventory': inventory_opt,
                'service': service_opt
            },
            'projections': [
                {
                    'month': p.month,
                    'total_savings': p.total_savings,
                    'monthly_cash_flow': p.monthly_cash_flow,
                    'cumulative_cash_flow': p.cumulative_cash_flow,
                    'roi_to_date': p.roi_to_date,
                    'payback_achieved': p.payback_achieved,
                    'labor_savings': p.labor_savings,
                    'quality_savings': p.quality_savings,
                    'inventory_savings': p.inventory_savings,
                    'service_savings': p.service_savings
                } for p in projections
            ],
            'break_even_analysis': break_even,
            'summary': {
                'total_annual_savings': total_annual_savings,
                'total_implementation_cost': total_implementation_cost
            },
            'metrics': {
                'total_current_costs': baseline.cost_breakdown.total_costs(),
                'total_optimized_costs': baseline.cost_breakdown.total_costs() - total_annual_savings,
                'total_savings': total_annual_savings,
                'payback_months': break_even.get('break_even_month', 12),
                'roi_percentage': break_even.get('final_roi_percentage', 0),
                'confidence_score': _calculate_confidence_score(baseline, questionnaire_analysis)
            }
        }
        
        # Save simulation to database
        simulation = Simulation(
            company_id=company_id,
            baseline_data=simulation_data['baseline'],
            optimized_data=simulation_data,
            assumptions=automation_levels
        )
        
        db.session.add(simulation)
        db.session.commit()
        
        logger.info(f"Enhanced simulation created for company {company_id}: {simulation.id}")
        
        return jsonify({
            'success': True,
            'simulation_id': simulation.id,
            'data': simulation_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Enhanced simulation creation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_simulation_bp.route('/api/companies/<int:company_id>/enhanced-simulation', methods=['GET'])
@cross_origin()
def get_enhanced_simulation(company_id):
    """Get the latest enhanced simulation for a company."""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'success': False, 'error': 'Company not found'}), 404
        
        # Get latest enhanced simulation
        simulation = Simulation.query.filter_by(company_id=company_id).order_by(Simulation.created_at.desc()).first()
        
        if not simulation:
            return jsonify({'success': False, 'error': 'No enhanced simulation found'}), 404
        
        return jsonify({
            'success': True,
            'data': simulation.optimized_data
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get enhanced simulation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_simulation_bp.route('/api/enhanced-simulations/<int:simulation_id>/adjust', methods=['POST'])
@cross_origin()
def adjust_enhanced_simulation(simulation_id):
    """Handle real-time adjustments for enhanced simulation."""
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
        
        # Create enhanced baseline from stored data
        company_data = {
            'financial_data': {
                'revenue': baseline_data['revenue'],
                'cogs': baseline_data['cogs'],
                'labor_costs': baseline_data['labor_costs'],
                'overhead_costs': baseline_data['overhead_costs']
            },
            'company_profile': {
                'production_volume': f"{baseline_data['production_volume']} units/year",
                'employee_count': str(baseline_data['employee_count']),
                'automation_level': 'Some automated tools'
            }
        }
        
        enhanced_baseline = enhanced_engine.create_enhanced_baseline(company_data)
        
        # Extract new automation levels
        automation_levels = {
            'labor': data.get('labor_automation', 50) / 100,
            'quality': data.get('quality_automation', 50) / 100,
            'inventory': data.get('inventory_automation', 50) / 100,
            'service': data.get('service_automation', 50) / 100
        }
        
        # Calculate new optimizations
        labor_opt = enhanced_engine.calculate_labor_optimization(enhanced_baseline, automation_levels['labor'])
        quality_opt = enhanced_engine.calculate_quality_optimization(enhanced_baseline, automation_levels['quality'])
        inventory_opt = enhanced_engine.calculate_inventory_optimization(enhanced_baseline, automation_levels['inventory'])
        service_opt = enhanced_engine.calculate_service_automation(enhanced_baseline, automation_levels['service'])
        
        # Generate quick projections (12 months)
        projections = enhanced_engine.generate_monthly_projections(enhanced_baseline, automation_levels, 12)
        break_even = enhanced_engine.analyze_break_even(projections)
        
        # Calculate summary metrics
        total_annual_savings = sum([
            labor_opt['total_annual_savings'],
            quality_opt['total_annual_savings'],
            inventory_opt['total_annual_savings'],
            service_opt['total_annual_savings']
        ])
        
        total_implementation = sum([
            labor_opt['implementation_cost'] + labor_opt['training_cost'],
            quality_opt['quality_system_cost'] + quality_opt['training_cost'],
            inventory_opt['system_cost'] + inventory_opt['training_cost'],
            service_opt['automation_platform_cost'] + service_opt['setup_cost']
        ])
        
        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'adjustments': automation_levels,
            'results': {
                'optimizations': {
                    'labor': labor_opt,
                    'quality': quality_opt,
                    'inventory': inventory_opt,
                    'service': service_opt
                },
                'summary': {
                    'total_annual_savings': total_annual_savings,
                    'total_implementation_cost': total_implementation,
                    'net_benefit_year_1': total_annual_savings - total_implementation,
                    'overall_roi_year_1': ((total_annual_savings - total_implementation) / total_implementation * 100) if total_implementation > 0 else 0,
                    'monthly_savings': total_annual_savings / 12,
                    'break_even_month': break_even['break_even_month']
                },
                'projections': [
                    {
                        'month': p.month,
                        'monthly_savings': p.total_savings,
                        'cumulative_cash_flow': p.cumulative_cash_flow,
                        'roi_to_date': p.roi_to_date
                    } for p in projections[:6]  # First 6 months for quick view
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Enhanced simulation adjustment failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _calculate_confidence_score(baseline, questionnaire_analysis):
    """Calculate confidence score based on data quality and completeness."""
    base_score = 75  # Base confidence
    
    # Adjust based on company size (more data = higher confidence)
    if baseline.employee_count > 100:
        base_score += 10
    elif baseline.employee_count < 25:
        base_score -= 5
        
    # Adjust based on questionnaire analysis availability
    if questionnaire_analysis:
        base_score += 15  # Enhanced questionnaire data available
        
    # Adjust based on financial data completeness
    if baseline.revenue > 1000000 and baseline.labor_costs > 0:
        base_score += 5  # Good financial data
        
    return min(95, max(60, base_score))  # Keep between 60-95%