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
                'text': 'What type of products do you manufacture?',
                'type': 'select',
                'options': ['Metal/Machined Parts', 'Plastic/Injection Molded Items', 'Electronics/Assemblies', 'Food & Beverage Products', 'Textiles/Apparel', 'Mixed/Other'],
                'required': True
            },
            {
                'id': 'q2',
                'text': 'What is your primary production method?',
                'type': 'select',
                'options': ['Make-to-order (custom/bespoke)', 'Make-to-stock (standard products)', 'Batch production', 'Continuous flow'],
                'required': True
            },
            {
                'id': 'q3',
                'text': 'How many production employees do you have?',
                'type': 'select',
                'options': ['1-10', '11-25', '26-50', '51-100', '100+'],
                'required': True
            },
            {
                'id': 'q4',
                'text': 'What percentage of products require rework or fail quality checks?',
                'type': 'select',
                'options': ['Less than 1%', '1-3%', '3-5%', '5-10%', 'More than 10%'],
                'required': True
            },
            {
                'id': 'q5',
                'text': 'What is your average monthly production volume?',
                'type': 'select',
                'options': ['Under 100 units', '100-1,000 units', '1,000-10,000 units', '10,000-100,000 units', 'Over 100,000 units'],
                'required': True
            },
            {
                'id': 'q6',
                'text': 'How much unplanned equipment downtime do you experience monthly?',
                'type': 'select',
                'options': ['Less than 4 hours', '4-16 hours', '16-40 hours', '40-80 hours', 'More than 80 hours'],
                'required': True
            },
            {
                'id': 'q7',
                'text': 'What percentage of your revenue comes from repeat customers?',
                'type': 'select',
                'options': ['Less than 20%', '20-40%', '40-60%', '60-80%', 'More than 80%'],
                'required': True
            },
            {
                'id': 'q8',
                'text': 'How do you currently track inventory and production?',
                'type': 'select',
                'options': ['Paper/Manual', 'Spreadsheets', 'Basic software', 'ERP system', 'Real-time digital tracking'],
                'required': True
            },
            {
                'id': 'q9',
                'text': 'What is your average inventory holding period?',
                'type': 'select',
                'options': ['Less than 1 week', '1-2 weeks', '2-4 weeks', '1-2 months', 'More than 2 months'],
                'required': True
            },
            {
                'id': 'q10',
                'text': 'What are your top 2-3 operational pain points?',
                'type': 'textarea',
                'placeholder': 'Example: "Finding skilled workers", "Meeting delivery deadlines", "Material waste"',
                'required': True
            },
            {
                'id': 'q11',
                'text': 'Approximately what percentage of your total costs are:',
                'type': 'cost_breakdown',
                'required': True,
                'fields': [
                    {'name': 'labor', 'label': 'Labor'},
                    {'name': 'materials', 'label': 'Materials'},
                    {'name': 'overhead', 'label': 'Overhead'}
                ]
            },
            {
                'id': 'q12',
                'text': 'What specific measurable outcome would make an AI investment worthwhile for you?',
                'type': 'textarea',
                'placeholder': 'Example: "Reduce overtime by 50%", "Cut defects in half", "Increase output 30%"',
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