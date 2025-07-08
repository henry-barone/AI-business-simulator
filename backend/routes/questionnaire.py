from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import uuid
from datetime import datetime
from typing import Dict, Any

from models.questionnaire import db, QuestionnaireSession, QuestionnaireResponse, QuestionnaireAnalysis
from services.questionnaire_flow import QuestionnaireFlow
from services.ai_analyzer import AIAnalyzer

questionnaire_bp = Blueprint('questionnaire', __name__)
flow = QuestionnaireFlow()
ai_analyzer = AIAnalyzer()

@questionnaire_bp.route('/api/questionnaire/start', methods=['POST'])
@cross_origin()
def start_questionnaire():
    """Start a new questionnaire session."""
    try:
        data = request.get_json() or {}
        company_id = data.get('company_id')
        
        # Create new session
        session_id = str(uuid.uuid4())
        session = QuestionnaireSession(
            id=session_id,
            company_id=company_id,
            current_question='START'
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Get first question
        first_question = flow.get_question('START')
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'question': first_question
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@questionnaire_bp.route('/api/questionnaire/<session_id>/answer', methods=['POST'])
@cross_origin()
def submit_answer(session_id: str):
    """Submit an answer and get the next question."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        answer = data.get('answer')
        if answer is None:
            return jsonify({'success': False, 'error': 'Answer is required'}), 400
        
        # Get session
        session = QuestionnaireSession.query.filter_by(id=session_id).first()
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        if session.status != 'in_progress':
            return jsonify({'success': False, 'error': 'Session is not active'}), 400
        
        current_question_id = session.current_question
        
        # Validate answer
        if not flow.validate_answer(current_question_id, answer):
            return jsonify({'success': False, 'error': 'Invalid answer for this question'}), 400
        
        # Get current question for storing response
        current_question = flow.get_question(current_question_id)
        
        # Store response
        response = QuestionnaireResponse(
            session_id=session_id,
            question_id=current_question_id,
            question_text=current_question['question'],
            answer=str(answer),
            answer_type=current_question['type']
        )
        
        db.session.add(response)
        
        # Check if questionnaire is complete
        if flow.is_complete(current_question_id, answer):
            session.status = 'completed'
            session.completed_at = datetime.utcnow()
            db.session.commit()
            
            # Trigger AI analysis
            try:
                ai_analyzer.analyze_session(session_id)
            except Exception as e:
                print(f"AI analysis failed: {e}")
            
            return jsonify({
                'success': True,
                'completed': True,
                'message': 'Questionnaire completed successfully'
            }), 200
        
        # Get next question
        next_question_id = flow.get_next_question_id(current_question_id, answer)
        if not next_question_id:
            return jsonify({'success': False, 'error': 'Unable to determine next question'}), 500
        
        # Update session
        session.current_question = next_question_id
        db.session.commit()
        
        # Get next question data
        next_question = flow.get_question(next_question_id)
        
        return jsonify({
            'success': True,
            'completed': False,
            'question': next_question
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@questionnaire_bp.route('/api/questionnaire/<session_id>/status', methods=['GET'])
@cross_origin()
def get_session_status(session_id: str):
    """Get the current status of a questionnaire session."""
    try:
        session = QuestionnaireSession.query.filter_by(id=session_id).first()
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Get current question if session is in progress
        current_question = None
        if session.status == 'in_progress':
            current_question = flow.get_question(session.current_question)
        
        # Get response count
        response_count = QuestionnaireResponse.query.filter_by(session_id=session_id).count()
        
        return jsonify({
            'success': True,
            'session': {
                'id': session.id,
                'status': session.status,
                'started_at': session.started_at.isoformat(),
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'response_count': response_count,
                'current_question': current_question
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@questionnaire_bp.route('/api/questionnaire/<session_id>/responses', methods=['GET'])
@cross_origin()
def get_session_responses(session_id: str):
    """Get all responses for a session."""
    try:
        session = QuestionnaireSession.query.filter_by(id=session_id).first()
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        responses = QuestionnaireResponse.query.filter_by(session_id=session_id).order_by(QuestionnaireResponse.answered_at).all()
        
        response_data = []
        for resp in responses:
            response_data.append({
                'question_id': resp.question_id,
                'question_text': resp.question_text,
                'answer': resp.answer,
                'answer_type': resp.answer_type,
                'answered_at': resp.answered_at.isoformat(),
                'ai_analyzed': resp.ai_analyzed,
                'extracted_insights': resp.extracted_insights
            })
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'responses': response_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@questionnaire_bp.route('/api/questionnaire/<session_id>/analysis', methods=['GET'])
@cross_origin()
def get_session_analysis(session_id: str):
    """Get AI analysis results for a completed session."""
    try:
        session = QuestionnaireSession.query.filter_by(id=session_id).first()
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        analysis = QuestionnaireAnalysis.query.filter_by(session_id=session_id).first()
        if not analysis:
            return jsonify({'success': False, 'error': 'Analysis not found or not yet completed'}), 404
        
        return jsonify({
            'success': True,
            'analysis': {
                'company_type': analysis.company_type,
                'industry': analysis.industry,
                'size_category': analysis.size_category,
                'production_volume': analysis.production_volume,
                'pain_points': analysis.get_pain_points(),
                'opportunities': analysis.get_opportunities(),
                'automation_level': analysis.automation_level,
                'priority_areas': analysis.get_priority_areas(),
                'confidence_score': analysis.confidence_score,
                'analyzed_at': analysis.analyzed_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@questionnaire_bp.route('/api/questionnaire/flow', methods=['GET'])
@cross_origin()
def get_questionnaire_flow():
    """Get the complete questionnaire flow for reference."""
    try:
        all_questions = flow.get_all_questions()
        return jsonify({
            'success': True,
            'questions': all_questions
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@questionnaire_bp.route('/next', methods=['POST'])
@cross_origin()
def get_next_question():
    """Get the next question in the dynamic questionnaire flow."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        company_id = data.get('companyId')
        previous_answers = data.get('previousAnswers', {})
        
        # Enhanced 12-question comprehensive business assessment
        questions = [
            {
                'id': 'q1',
                'text': 'What type of products or services does your company primarily provide?',
                'type': 'select',
                'options': ['Metal Parts & Components', 'Plastic/Polymer Products', 'Electronics & Technology', 'Textiles & Apparel', 'Food & Beverage', 'Chemical Products', 'Automotive Parts', 'Medical Devices', 'Construction Materials', 'Other Manufacturing'],
                'required': True
            },
            {
                'id': 'q2',
                'text': 'What is your typical daily production volume?',
                'type': 'select',
                'options': ['Under 100 units/day', '100-500 units/day', '500-2,000 units/day', '2,000-10,000 units/day', '10,000-50,000 units/day', 'Over 50,000 units/day'],
                'required': True
            },
            {
                'id': 'q3',
                'text': 'How many employees work in your manufacturing/production operations?',
                'type': 'select',
                'options': ['1-10 employees', '11-25 employees', '26-50 employees', '51-100 employees', '101-250 employees', '251-500 employees', 'Over 500 employees'],
                'required': True
            },
            {
                'id': 'q4',
                'text': 'What is your company\'s annual revenue range?',
                'type': 'select',
                'options': ['Under $500K', '$500K - $2M', '$2M - $10M', '$10M - $50M', '$50M - $200M', 'Over $200M'],
                'required': True
            },
            {
                'id': 'q5',
                'text': 'What are your biggest operational challenges and pain points? (Please describe in detail)',
                'type': 'textarea',
                'placeholder': 'Describe specific challenges like quality issues, production bottlenecks, labor shortages, cost pressures, etc.',
                'required': True
            },
            {
                'id': 'q6',
                'text': 'How do you currently handle quality control and inspection?',
                'type': 'select',
                'options': ['100% manual inspection', 'Statistical sampling with manual checks', 'Some automated testing equipment', 'Advanced automated inspection systems', 'AI-powered quality control', 'No formal quality control process'],
                'required': True
            },
            {
                'id': 'q7',
                'text': 'What percentage of your production time is lost to defects, rework, or equipment downtime?',
                'type': 'select',
                'options': ['Less than 5%', '5-10%', '10-20%', '20-30%', '30-50%', 'More than 50%', 'Not sure/No tracking'],
                'required': True
            },
            {
                'id': 'q8',
                'text': 'How do you currently manage inventory, materials, and supply chain?',
                'type': 'select',
                'options': ['Manual tracking (spreadsheets/paper)', 'Basic inventory software', 'ERP system integration', 'Advanced supply chain management system', 'AI-powered demand forecasting', 'Just-in-time/lean approach'],
                'required': True
            },
            {
                'id': 'q9',
                'text': 'What is your current level of automation in production processes?',
                'type': 'select',
                'options': ['Fully manual operations', 'Basic tools and equipment only', 'Some automated machinery', 'Moderate automation (30-50% of processes)', 'Highly automated (50-80% of processes)', 'Nearly fully automated (80%+ of processes)'],
                'required': True
            },
            {
                'id': 'q10',
                'text': 'How many customer service inquiries, complaints, or support requests do you handle per week?',
                'type': 'select',
                'options': ['Fewer than 10', '10-25', '25-50', '50-100', '100-250', 'More than 250', 'No formal tracking'],
                'required': True
            },
            {
                'id': 'q11',
                'text': 'What is your typical annual budget for operational improvements and technology investments?',
                'type': 'select',
                'options': ['Under $25,000', '$25,000 - $75,000', '$75,000 - $200,000', '$200,000 - $500,000', '$500,000 - $1M', '$1M - $5M', 'Over $5M'],
                'required': True
            },
            {
                'id': 'q12',
                'text': 'Which specific areas would you most like to improve through automation or AI? What are your priorities and expected outcomes?',
                'type': 'textarea',
                'placeholder': 'Describe your automation priorities: labor efficiency, quality control, inventory management, customer service, predictive maintenance, etc. Include expected benefits.',
                'required': True
            }
        ]
        
        # Determine which question to return based on previous answers
        answered_count = len(previous_answers)
        
        if answered_count >= len(questions):
            # All questions answered, questionnaire complete
            return jsonify({
                'data': {
                    'completed': True,
                    'message': 'Questionnaire completed successfully'
                }
            }), 200
        
        # Return the next question
        next_question = questions[answered_count]
        
        return jsonify({
            'data': {
                'question': next_question
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@questionnaire_bp.route('/api/questionnaire/<session_id>/restart', methods=['POST'])
@cross_origin()
def restart_questionnaire(session_id: str):
    """Restart a questionnaire session."""
    try:
        session = QuestionnaireSession.query.filter_by(id=session_id).first()
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Clear existing responses
        QuestionnaireResponse.query.filter_by(session_id=session_id).delete()
        
        # Clear existing analysis
        QuestionnaireAnalysis.query.filter_by(session_id=session_id).delete()
        
        # Reset session
        session.current_question = 'START'
        session.status = 'in_progress'
        session.completed_at = None
        session.started_at = datetime.utcnow()
        
        db.session.commit()
        
        # Get first question
        first_question = flow.get_question('START')
        
        return jsonify({
            'success': True,
            'message': 'Questionnaire restarted',
            'question': first_question
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500