from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from typing import Dict, Any

from services.ai_service import AIService
from services.pl_analyzer import PLAnalyzer
from models.questionnaire import QuestionnaireSession, QuestionnaireResponse, QuestionnaireAnalysis
from models.questionnaire import db

logger = logging.getLogger(__name__)

ai_analysis_bp = Blueprint('ai_analysis', __name__)
ai_service = AIService()
pl_analyzer = PLAnalyzer()

@ai_analysis_bp.route('/api/ai/analyze-pain-points', methods=['POST'])
@cross_origin()
def analyze_pain_points():
    """Analyze text responses to extract manufacturing pain points."""
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
        
        return jsonify({
            'success': True,
            'pain_points': pain_points_data,
            'total_found': len(pain_points_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Pain point analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_analysis_bp.route('/api/ai/generate-recommendations', methods=['POST'])
@cross_origin()
def generate_recommendations():
    """Generate AI-powered manufacturing recommendations."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        company_data = data.get('company_data')
        if not company_data:
            return jsonify({'success': False, 'error': 'Company data is required'}), 400
        
        # Generate recommendations
        recommendations = ai_service.generate_recommendations(company_data)
        
        # Convert to dictionaries
        recommendations_data = [ai_service._recommendation_to_dict(rec) for rec in recommendations]
        
        return jsonify({
            'success': True,
            'recommendations': recommendations_data,
            'total_generated': len(recommendations_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_analysis_bp.route('/api/ai/estimate-impact', methods=['POST'])
@cross_origin()
def estimate_impact():
    """Estimate financial impact of a recommendation."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        recommendation_data = data.get('recommendation')
        company_data = data.get('company_data')
        
        if not recommendation_data or not company_data:
            return jsonify({'success': False, 'error': 'Recommendation and company data are required'}), 400
        
        # Convert dict back to Recommendation object
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
        
        # Estimate financial impact
        impact = ai_service.estimate_impact(recommendation, company_data)
        
        # Convert to dictionary
        impact_data = ai_service._financial_impact_to_dict(impact)
        
        return jsonify({
            'success': True,
            'financial_impact': impact_data
        }), 200
        
    except Exception as e:
        logger.error(f"Impact estimation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_analysis_bp.route('/api/ai/comprehensive-analysis', methods=['POST'])
@cross_origin()
def comprehensive_analysis():
    """Run comprehensive AI analysis combining questionnaire and financial data."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        session_id = data.get('session_id')
        financial_data = data.get('financial_data')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID is required'}), 400
        
        # Get questionnaire data
        session = QuestionnaireSession.query.filter_by(id=session_id).first()
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        responses = QuestionnaireResponse.query.filter_by(session_id=session_id).all()
        
        # Prepare questionnaire data
        questionnaire_data = {
            'company_profile': {},
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
        
        # Use provided financial data or extract from session
        if not financial_data:
            financial_data = {
                'revenue': 500000,  # Default values
                'labor_costs': 200000,
                'overhead_costs': 100000,
                'cogs': 250000
            }
        
        # Run comprehensive analysis
        analysis = ai_service.analyze_comprehensive(questionnaire_data, financial_data)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_analysis_bp.route('/api/ai/analyze-pl-and-questionnaire', methods=['POST'])
@cross_origin()
def analyze_pl_and_questionnaire():
    """Analyze uploaded P&L file combined with questionnaire responses."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        session_id = data.get('session_id')
        pl_file_path = data.get('pl_file_path')
        
        if not session_id or not pl_file_path:
            return jsonify({'success': False, 'error': 'Session ID and P&L file path are required'}), 400
        
        # Parse P&L file
        pl_data = pl_analyzer.parse_file(pl_file_path)
        if pl_data.get('error'):
            return jsonify({'success': False, 'error': f"P&L parsing failed: {pl_data['error']}"}), 400
        
        # Extract financial data
        financial_data = {
            'revenue': pl_data.get('revenue', 0),
            'labor_costs': pl_data.get('labor_costs', 0),
            'overhead_costs': pl_data.get('overhead_costs', 0),
            'cogs': pl_data.get('cogs', 0)
        }
        
        # Get questionnaire data
        session = QuestionnaireSession.query.filter_by(id=session_id).first()
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        responses = QuestionnaireResponse.query.filter_by(session_id=session_id).all()
        
        # Prepare questionnaire data
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
        
        # Run comprehensive analysis
        analysis = ai_service.analyze_comprehensive(questionnaire_data, financial_data)
        
        # Add P&L analysis results
        analysis['pl_analysis'] = {
            'parsed_data': pl_data,
            'confidence_score': pl_data.get('confidence_score', 0),
            'validation': pl_analyzer.validate_data(pl_data)
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"P&L and questionnaire analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_analysis_bp.route('/api/ai/capabilities', methods=['GET'])
@cross_origin()
def get_ai_capabilities():
    """Get information about AI service capabilities and status."""
    try:
        capabilities = {
            'openai_available': ai_service.openai_client is not None,
            'anthropic_available': ai_service.anthropic_client is not None,
            'fallback_analysis': True,
            'features': {
                'pain_point_analysis': True,
                'recommendation_generation': True,
                'financial_impact_estimation': True,
                'comprehensive_analysis': True,
                'pl_integration': True
            },
            'manufacturing_categories': list(ai_service.manufacturing_categories.keys()),
            'supported_file_formats': ['.csv', '.xlsx', '.xls', '.pdf']
        }
        
        return jsonify({
            'success': True,
            'capabilities': capabilities
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get AI capabilities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500