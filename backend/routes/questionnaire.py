from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from models import db
from models.company import Company
from models.simulation import QuestionnaireResponse

questionnaire_bp = Blueprint('questionnaire', __name__)

@questionnaire_bp.route('/submit', methods=['POST'])
def submit_questionnaire():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        company_id = data.get('company_id')
        responses = data.get('responses', [])
        
        if not company_id:
            return jsonify({'error': 'Company ID required'}), 400
        
        if not responses:
            return jsonify({'error': 'No responses provided'}), 400
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        saved_responses = []
        
        for response_data in responses:
            question_id = response_data.get('question_id')
            answer = response_data.get('answer')
            
            if not question_id or answer is None:
                continue
            
            # Check if response already exists, update if it does
            existing_response = QuestionnaireResponse.query.filter_by(
                company_id=company_id,
                question_id=question_id
            ).first()
            
            if existing_response:
                existing_response.answer = answer
                existing_response.answered_at = datetime.utcnow()
                saved_responses.append(existing_response)
            else:
                new_response = QuestionnaireResponse(
                    company_id=company_id,
                    question_id=question_id,
                    answer=answer
                )
                db.session.add(new_response)
                saved_responses.append(new_response)
        
        db.session.commit()
        
        current_app.logger.info(f"Questionnaire submitted for company {company_id}: {len(saved_responses)} responses")
        
        return jsonify({
            'message': 'Questionnaire submitted successfully',
            'company_id': company_id,
            'responses_saved': len(saved_responses),
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Questionnaire submission error: {e}")
        return jsonify({'error': 'Submission failed'}), 500

@questionnaire_bp.route('/<int:company_id>', methods=['GET'])
def get_questionnaire_responses(company_id):
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        responses = QuestionnaireResponse.query.filter_by(company_id=company_id).all()
        
        response_data = []
        for response in responses:
            response_data.append(response.to_dict())
        
        return jsonify({
            'company_id': company_id,
            'responses': response_data,
            'total_responses': len(response_data),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get questionnaire responses error: {e}")
        return jsonify({'error': 'Failed to retrieve responses'}), 500

@questionnaire_bp.route('/questions', methods=['GET'])
def get_questions():
    try:
        # Placeholder question set - customize based on business needs
        questions = [
            {
                'id': 'business_model',
                'text': 'What is your primary business model?',
                'type': 'multiple_choice',
                'options': ['B2B SaaS', 'E-commerce', 'Service-based', 'Manufacturing', 'Other']
            },
            {
                'id': 'revenue_streams',
                'text': 'What are your main revenue streams?',
                'type': 'text',
                'placeholder': 'Describe your revenue streams...'
            },
            {
                'id': 'customer_segments',
                'text': 'Who are your primary customer segments?',
                'type': 'text',
                'placeholder': 'Describe your customer segments...'
            },
            {
                'id': 'growth_challenges',
                'text': 'What are your biggest growth challenges?',
                'type': 'multiple_choice',
                'options': ['Customer acquisition', 'Operational efficiency', 'Cost management', 'Market expansion', 'Product development']
            },
            {
                'id': 'optimization_goals',
                'text': 'What would you like to optimize?',
                'type': 'checkbox',
                'options': ['Revenue growth', 'Cost reduction', 'Profit margins', 'Operational efficiency', 'Market share']
            }
        ]
        
        return jsonify({
            'questions': questions,
            'total_questions': len(questions),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get questions error: {e}")
        return jsonify({'error': 'Failed to retrieve questions'}), 500