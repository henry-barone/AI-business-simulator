from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from datetime import datetime
import logging
from typing import Dict, Any, List

from models import db
from models.company import Company
from models.simulation import Simulation
from models.questionnaire import QuestionnaireSession, QuestionnaireResponse as QResponse
from services.ai_service import AIService

logger = logging.getLogger(__name__)

recommendations_bp = Blueprint('recommendations', __name__)
ai_service = AIService()

@recommendations_bp.route('/api/companies/<int:company_id>/recommendations', methods=['GET'])
@cross_origin()
def get_company_recommendations(company_id):
    """Get AI-generated recommendations for a company."""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'success': False, 'error': 'Company not found'}), 404
        
        # Get latest simulation
        simulation = Simulation.query.filter_by(company_id=company_id).order_by(Simulation.created_at.desc()).first()
        
        if not simulation:
            return jsonify({
                'success': False, 
                'error': 'No simulation found for company. Create a simulation first.',
                'company_id': company_id
            }), 404
        
        # Check if simulation has AI analysis with recommendations
        optimized_data = simulation.optimized_data or {}
        ai_analysis = optimized_data.get('ai_analysis', {})
        
        if not ai_analysis.get('recommendations'):
            return jsonify({
                'success': False,
                'error': 'No AI recommendations found in simulation. Run simulation analysis first.',
                'simulation_id': simulation.id
            }), 404
        
        recommendations = ai_analysis['recommendations']
        pain_points = ai_analysis.get('pain_points', [])
        summary = ai_analysis.get('summary', {})
        
        # Enhance recommendations with ROI data from simulation
        enhanced_recommendations = []
        for rec_data in recommendations:
            recommendation = rec_data['recommendation']
            financial_impact = rec_data['financial_impact']
            
            enhanced_rec = {
                'id': len(enhanced_recommendations) + 1,  # Generate simple ID
                'title': recommendation['title'],
                'description': recommendation['description'],
                'category': recommendation['category'],
                'priority': recommendation['priority'],
                'implementation_effort': recommendation['implementation_effort'],
                'technology_type': recommendation['technology_type'],
                'estimated_timeline': recommendation['estimated_timeline'],
                'target_pain_points': recommendation['target_pain_points'],
                'confidence': recommendation['confidence'],
                'financial_impact': {
                    'annual_savings': financial_impact['cost_savings_annual'],
                    'implementation_cost': financial_impact['implementation_cost'],
                    'roi_percentage': financial_impact['roi_percentage'],
                    'payback_months': financial_impact['payback_months'],
                    'revenue_impact': financial_impact['revenue_impact'],
                    'cost_breakdown': financial_impact['cost_breakdown'],
                    'assumptions': financial_impact['assumptions'],
                    'confidence': financial_impact['confidence']
                }
            }
            enhanced_recommendations.append(enhanced_rec)
        
        # Sort by ROI percentage (descending)
        enhanced_recommendations.sort(key=lambda x: x['financial_impact']['roi_percentage'], reverse=True)
        
        return jsonify({
            'success': True,
            'company_id': company_id,
            'simulation_id': simulation.id,
            'recommendations': enhanced_recommendations,
            'pain_points': pain_points,
            'summary': {
                'total_recommendations': len(enhanced_recommendations),
                'total_pain_points': len(pain_points),
                'best_roi': enhanced_recommendations[0]['financial_impact']['roi_percentage'] if enhanced_recommendations else 0,
                'total_potential_savings': sum(rec['financial_impact']['annual_savings'] for rec in enhanced_recommendations),
                'total_implementation_cost': sum(rec['financial_impact']['implementation_cost'] for rec in enhanced_recommendations),
                'analysis_timestamp': ai_analysis.get('analysis_timestamp')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get company recommendations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/api/companies/<int:company_id>/recommendations/generate', methods=['POST'])
@cross_origin()
def generate_company_recommendations(company_id):
    """Generate fresh AI recommendations for a company using questionnaire and financial data."""
    try:
        data = request.get_json() or {}
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'success': False, 'error': 'Company not found'}), 404
        
        # Get questionnaire session
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'Questionnaire session ID required'}), 400
        
        session = QuestionnaireSession.query.filter_by(id=session_id).first()
        if not session:
            return jsonify({'success': False, 'error': 'Questionnaire session not found'}), 404
        
        # Get financial data
        financial_data = data.get('financial_data')
        if not financial_data:
            # Try to get from latest simulation
            simulation = Simulation.query.filter_by(company_id=company_id).order_by(Simulation.created_at.desc()).first()
            if simulation and simulation.baseline_data:
                financial_data = {
                    'revenue': simulation.baseline_data.get('revenue', 0),
                    'cogs': simulation.baseline_data.get('cogs', 0),
                    'labor_costs': simulation.baseline_data.get('labor_costs', 0),
                    'overhead_costs': simulation.baseline_data.get('overhead_costs', 0)
                }
            else:
                return jsonify({'success': False, 'error': 'Financial data required'}), 400
        
        # Get questionnaire responses
        responses = QResponse.query.filter_by(session_id=session_id).all()
        
        # Build questionnaire data
        questionnaire_data = {
            'company_profile': {'industry': 'Manufacturing'},
            'responses': []
        }
        
        for resp in responses:
            response_dict = {
                'question_id': resp.question_id,
                'question_text': resp.question_text,
                'answer': resp.answer,
                'answer_type': resp.answer_type
            }
            questionnaire_data['responses'].append(response_dict)
            
            # Extract company profile
            if resp.question_id == 'START':
                questionnaire_data['company_profile']['product_type'] = resp.answer
            elif resp.question_id in ['VOLUME', 'GENERAL_1']:
                questionnaire_data['company_profile']['production_volume'] = resp.answer
            elif resp.question_id == 'EMPLOYEES':
                questionnaire_data['company_profile']['employee_count'] = resp.answer
            elif resp.question_id == 'AUTOMATION_CURRENT':
                questionnaire_data['company_profile']['automation_level'] = resp.answer
        
        # Run comprehensive AI analysis
        ai_analysis = ai_service.analyze_comprehensive(questionnaire_data, financial_data)
        
        if 'error' in ai_analysis:
            return jsonify({
                'success': False,
                'error': f"AI analysis failed: {ai_analysis['error']}"
            }), 500
        
        # Extract recommendations
        recommendations = ai_analysis.get('recommendations', [])
        pain_points = ai_analysis.get('pain_points', [])
        
        return jsonify({
            'success': True,
            'company_id': company_id,
            'session_id': session_id,
            'analysis': ai_analysis,
            'recommendations': recommendations,
            'pain_points': pain_points,
            'summary': {
                'total_recommendations': len(recommendations),
                'total_pain_points': len(pain_points),
                'best_roi': recommendations[0]['financial_impact']['roi_percentage'] if recommendations else 0,
                'analysis_timestamp': ai_analysis.get('analysis_timestamp')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/api/recommendations/<int:recommendation_id>/impact', methods=['POST'])
@cross_origin()
def calculate_recommendation_impact(recommendation_id):
    """Calculate detailed financial impact for a specific recommendation."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Get recommendation data and company financial data
        recommendation_data = data.get('recommendation')
        company_data = data.get('company_data')
        
        if not recommendation_data or not company_data:
            return jsonify({
                'success': False, 
                'error': 'Recommendation and company data required'
            }), 400
        
        # Convert to Recommendation object
        from services.ai_service import Recommendation
        recommendation = Recommendation(
            title=recommendation_data.get('title', ''),
            description=recommendation_data.get('description', ''),
            category=recommendation_data.get('category', 'automation'),
            priority=recommendation_data.get('priority', 'medium'),
            implementation_effort=recommendation_data.get('implementation_effort', 'medium'),
            technology_type=recommendation_data.get('technology_type', 'software'),
            target_pain_points=recommendation_data.get('target_pain_points', []),
            estimated_timeline=recommendation_data.get('estimated_timeline', '6-12 months'),
            confidence=float(recommendation_data.get('confidence', 0.7))
        )
        
        # Calculate financial impact
        impact = ai_service.estimate_impact(recommendation, company_data)
        
        # Convert to dictionary
        impact_data = ai_service._financial_impact_to_dict(impact)
        
        return jsonify({
            'success': True,
            'recommendation_id': recommendation_id,
            'financial_impact': impact_data,
            'recommendation_title': recommendation.title
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to calculate recommendation impact: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/api/recommendations/analyze-text', methods=['POST'])
@cross_origin()
def analyze_text_for_pain_points():
    """Analyze free text to extract pain points and generate recommendations."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        text_response = data.get('text_response')
        context = data.get('context', {})
        
        if not text_response:
            return jsonify({'success': False, 'error': 'Text response is required'}), 400
        
        # Analyze pain points
        pain_points = ai_service.analyze_pain_points(text_response, context)
        
        # Convert to dictionaries
        pain_points_data = [ai_service._pain_point_to_dict(pp) for pp in pain_points]
        
        # Generate basic recommendations based on pain points
        mock_company_data = {
            'company_profile': context,
            'financial_data': {
                'revenue': context.get('revenue', 500000),
                'labor_costs': context.get('labor_costs', 200000),
                'overhead_costs': context.get('overhead_costs', 100000),
                'cogs': context.get('cogs', 250000)
            },
            'pain_points': pain_points
        }
        
        recommendations = ai_service.generate_recommendations(mock_company_data)
        recommendations_data = [ai_service._recommendation_to_dict(rec) for rec in recommendations]
        
        return jsonify({
            'success': True,
            'text_analyzed': text_response[:100] + '...' if len(text_response) > 100 else text_response,
            'pain_points': pain_points_data,
            'recommendations': recommendations_data,
            'summary': {
                'pain_points_found': len(pain_points_data),
                'recommendations_generated': len(recommendations_data),
                'context_provided': len(context) > 0
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to analyze text: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@recommendations_bp.route('/api/recommendations/batch-impact', methods=['POST'])
@cross_origin()
def calculate_batch_impact():
    """Calculate financial impact for multiple recommendations."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        recommendations_data = data.get('recommendations', [])
        company_data = data.get('company_data')
        
        if not recommendations_data or not company_data:
            return jsonify({
                'success': False,
                'error': 'Recommendations and company data required'
            }), 400
        
        # Calculate impact for each recommendation
        results = []
        total_savings = 0
        total_implementation_cost = 0
        
        for i, rec_data in enumerate(recommendations_data):
            try:
                # Convert to Recommendation object
                from services.ai_service import Recommendation
                recommendation = Recommendation(
                    title=rec_data.get('title', f'Recommendation {i+1}'),
                    description=rec_data.get('description', ''),
                    category=rec_data.get('category', 'automation'),
                    priority=rec_data.get('priority', 'medium'),
                    implementation_effort=rec_data.get('implementation_effort', 'medium'),
                    technology_type=rec_data.get('technology_type', 'software'),
                    target_pain_points=rec_data.get('target_pain_points', []),
                    estimated_timeline=rec_data.get('estimated_timeline', '6-12 months'),
                    confidence=float(rec_data.get('confidence', 0.7))
                )
                
                # Calculate impact
                impact = ai_service.estimate_impact(recommendation, company_data)
                impact_data = ai_service._financial_impact_to_dict(impact)
                
                results.append({
                    'recommendation': ai_service._recommendation_to_dict(recommendation),
                    'financial_impact': impact_data
                })
                
                total_savings += impact.cost_savings_annual
                total_implementation_cost += impact.implementation_cost
                
            except Exception as e:
                logger.warning(f"Failed to calculate impact for recommendation {i+1}: {e}")
                results.append({
                    'recommendation': rec_data,
                    'financial_impact': None,
                    'error': str(e)
                })
        
        # Sort by ROI
        successful_results = [r for r in results if r.get('financial_impact')]
        successful_results.sort(key=lambda x: x['financial_impact']['roi_percentage'], reverse=True)
        
        # Calculate portfolio metrics
        portfolio_roi = ((total_savings - total_implementation_cost) / total_implementation_cost * 100) if total_implementation_cost > 0 else 0
        
        return jsonify({
            'success': True,
            'results': results,
            'successful_calculations': len(successful_results),
            'failed_calculations': len(results) - len(successful_results),
            'portfolio_summary': {
                'total_annual_savings': total_savings,
                'total_implementation_cost': total_implementation_cost,
                'net_benefit': total_savings - total_implementation_cost,
                'portfolio_roi_percentage': portfolio_roi,
                'best_individual_roi': successful_results[0]['financial_impact']['roi_percentage'] if successful_results else 0
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to calculate batch impact: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500