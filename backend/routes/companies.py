from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from models import db
from models.company import Company
from models.simulation import PLStatement
from services.pl_analyzer import PLAnalyzer

# Import new utilities but make them optional for backward compatibility
try:
    from services.auth_service import jwt_required, rate_limit, optional_jwt
    from utils.api_response import (
        success_response, error_response, validation_error_response, 
        not_found_response, internal_error_response
    )
    from utils.validators import validate_financial_data, sanitize_string
    ENHANCED_FEATURES = True
except ImportError:
    ENHANCED_FEATURES = False

companies_bp = Blueprint('companies', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@companies_bp.route('', methods=['POST'])
def create_company():
    """Create a new company with backward compatibility."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name')
        industry = data.get('industry')
        email = data.get('email')
        email_consent = data.get('emailConsent', False)
        
        if not name:
            return jsonify({'error': 'Company name is required'}), 400
        
        # Sanitize input if enhanced features available
        if ENHANCED_FEATURES:
            name = sanitize_string(name, 100)
        
        # Check for duplicate company names and handle by adding timestamp
        try:
            # Try to check for existing company, but handle if email columns don't exist yet
            try:
                existing_company = Company.query.filter_by(name=name).first()
            except Exception as column_error:
                # If email columns don't exist, skip duplicate check for now
                current_app.logger.warning(f"Column error (likely missing email fields): {column_error}")
                existing_company = None
                
            if existing_company:
                # Generate unique name by appending timestamp
                from datetime import datetime
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                name = f"{name}_{timestamp}"
                current_app.logger.info(f"Duplicate company name detected, using unique name: {name}")
        except Exception as query_error:
            current_app.logger.error(f"Database query error: {query_error}")
            return jsonify({'error': 'Database query failed', 'details': str(query_error)}), 500
        
        # Create company - only use fields that exist in the model
        try:
            # Try to create with email fields, fall back to basic fields if columns don't exist
            try:
                company = Company(
                    name=name, 
                    industry=industry,
                    email=email,
                    email_consent=email_consent
                )
            except Exception as create_error:
                current_app.logger.warning(f"Creating company without email fields: {create_error}")
                company = Company(name=name, industry=industry)
                
            db.session.add(company)
            db.session.commit()
        except Exception as db_error:
            db.session.rollback()
            current_app.logger.error(f"Database error: {db_error}")
            raise db_error
        
        current_app.logger.info(f"Company created: {name} (ID: {company.id})")
        
        # Prepare response data using enhanced format if available
        if ENHANCED_FEATURES:
            return success_response(
                data={
                    'id': company.id,
                    'name': company.name,
                    'industry': company.industry,
                    'created_at': company.created_at.isoformat() if company.created_at else None
                },
                message="Company created successfully",
                status_code=201
            )
        else:
            # Legacy response format
            return jsonify({
                'data': {
                    'id': str(company.id),
                    'name': company.name,
                    'industry': company.industry,
                    'created_at': company.created_at.isoformat() if company.created_at else None
                }
            }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Company creation error: {e}")
        # Always use basic JSON response for errors to avoid secondary issues
        return jsonify({'error': 'Failed to create company', 'details': str(e)}), 500

@companies_bp.route('/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get company details with backward compatibility."""
    try:
        company = Company.query.get(company_id)
        if not company:
            if ENHANCED_FEATURES:
                return not_found_response("Company")
            else:
                return jsonify({'error': 'Company not found'}), 404
        
        response_data = {
            'id': company.id,
            'name': company.name,
            'industry': company.industry,
            'created_at': company.created_at.isoformat() if company.created_at else None
        }
        
        if ENHANCED_FEATURES:
            return success_response(data=response_data)
        else:
            return jsonify({'data': response_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get company error: {e}")
        if ENHANCED_FEATURES:
            return internal_error_response("Failed to retrieve company")
        else:
            return jsonify({'error': 'Failed to retrieve company'}), 500

@companies_bp.route('/<int:company_id>/upload-pl', methods=['POST'])
def upload_pl_for_company(company_id):
    """Upload P&L statement for a specific company"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Verify company exists
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        if not (file and allowed_file(file.filename)):
            return jsonify({'error': 'Invalid file type. Supported formats: Excel (.xlsx, .xls), CSV, PDF'}), 400
        
        # Secure filename and save file
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER', '/tmp/uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Parse P&L data using intelligent analyzer
        analyzer = PLAnalyzer()
        current_app.logger.info(f"Starting P&L analysis for file: {filename}")
        
        parsed_data = analyzer.parse_file(filepath)
        validation_result = analyzer.validate_data(parsed_data)
        
        # Log parsing results
        current_app.logger.info(f"P&L parsing completed. Confidence: {parsed_data.get('confidence_score', 0):.2f}")
        
        # Check for parsing errors
        if parsed_data.get('error'):
            current_app.logger.error(f"P&L parsing failed: {parsed_data['error']}")
            return jsonify({
                'error': 'Failed to parse P&L data',
                'details': parsed_data['error'],
                'filename': filename
            }), 422
        
        # Create P&L statement with parsed data
        pl_statement = PLStatement(
            company_id=company_id,
            revenue=parsed_data.get('revenue', 0.0),
            cogs=parsed_data.get('cogs', 0.0),
            labor_costs=parsed_data.get('labor_costs', 0.0),
            overhead_costs=parsed_data.get('overhead_costs', 0.0),
            other_costs={
                'filename': filename,
                'filepath': filepath,
                'confidence_score': parsed_data.get('confidence_score', 0.0),
                'validation_errors': validation_result.get('errors', []),
                'validation_warnings': validation_result.get('warnings', []),
                'parsing_metadata': {
                    'file_type': file.filename.split('.')[-1].lower(),
                    'original_filename': file.filename,
                    'upload_timestamp': datetime.utcnow().isoformat()
                }
            }
        )
        
        db.session.add(pl_statement)
        db.session.commit()
        
        current_app.logger.info(f"P&L statement created with ID: {pl_statement.id} for company {company_id}")
        
        response_data = {
            'data': {
                'revenue': parsed_data.get('revenue', 0.0),
                'cogs': parsed_data.get('cogs', 0.0),
                'labor_costs': parsed_data.get('labor_costs', 0.0),
                'overhead': parsed_data.get('overhead_costs', 0.0),
                'pl_statement_id': pl_statement.id,
                'confidence_score': parsed_data.get('confidence_score', 0.0)
            }
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"P&L upload error: {str(e)}")
        return jsonify({
            'error': 'Upload failed',
            'details': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@companies_bp.route('/<int:company_id>/questionnaire', methods=['POST'])
def submit_questionnaire_answer(company_id):
    """Submit questionnaire answer for a company"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Verify company exists
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        question_id = data.get('questionId')
        answer = data.get('answer')
        
        if not question_id or not answer:
            return jsonify({'error': 'Question ID and answer are required'}), 400
        
        # Import here to avoid circular imports
        from models.simulation import QuestionnaireResponse
        
        # Create questionnaire response
        response = QuestionnaireResponse(
            company_id=company_id,
            question_id=question_id,
            answer=answer
        )
        
        db.session.add(response)
        db.session.commit()
        
        current_app.logger.info(f"Questionnaire answer submitted for company {company_id}, question {question_id}")
        
        return jsonify({
            'data': {
                'id': response.id,
                'company_id': company_id,
                'question_id': question_id,
                'answer': answer,
                'timestamp': response.answered_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Questionnaire submission error: {e}")
        return jsonify({'error': 'Failed to submit questionnaire answer'}), 500

@companies_bp.route('/<int:company_id>/simulation', methods=['GET'])
def get_simulation_for_company(company_id):
    """Get simulation data for a company"""
    try:
        # Verify company exists
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get the latest simulation for this company
        from models.simulation import Simulation
        simulation = Simulation.query.filter_by(company_id=company_id).order_by(Simulation.created_at.desc()).first()
        
        if not simulation:
            return jsonify({'error': 'No simulation found for this company'}), 404
        
        # Mock simulation data structure to match frontend expectations
        simulation_data = {
            'baseline': {
                'revenue': 100000,
                'costs': {
                    'labor': 40000,
                    'cogs': 30000,
                    'overhead': 20000
                }
            },
            'optimized': {
                'costs': {
                    'labor': 35000,
                    'cogs': 28000,
                    'overhead': 18000
                }
            },
            'timeline_projections': [
                {'month': 1, 'savings': 9000, 'cumulative': 9000},
                {'month': 2, 'savings': 9000, 'cumulative': 18000},
                {'month': 3, 'savings': 9000, 'cumulative': 27000},
                {'month': 4, 'savings': 9000, 'cumulative': 36000},
                {'month': 5, 'savings': 9000, 'cumulative': 45000},
                {'month': 6, 'savings': 9000, 'cumulative': 54000}
            ],
            'recommendations': [
                {
                    'type': 'automation',
                    'description': 'Implement automated inventory management',
                    'savings': 5000,
                    'cost': 10000,
                    'priority': 1
                },
                {
                    'type': 'efficiency',
                    'description': 'Optimize supply chain processes',
                    'savings': 3000,
                    'cost': 5000,
                    'priority': 2
                }
            ],
            'roi_metrics': {
                'total_investment': 15000,
                'payback_months': 3,
                'roi_percentage': 75
            }
        }
        
        return jsonify({
            'data': {
                'simulation': simulation_data
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get simulation error: {e}")
        return jsonify({'error': 'Failed to retrieve simulation data'}), 500