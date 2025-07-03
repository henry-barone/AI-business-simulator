from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from models import db
from models.company import Company
from models.simulation import PLStatement
from services.pl_analyzer import PLAnalyzer

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/pl-statement', methods=['POST'])
def upload_pl_statement():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        company_id = request.form.get('company_id')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not company_id:
            return jsonify({'error': 'Company ID required'}), 400
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            # Parse P&L data from uploaded file
            analyzer = PLAnalyzer()
            parsed_data = analyzer.parse_file(filepath)
            validation_result = analyzer.validate_data(parsed_data)
            
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
                    'raw_data': parsed_data.get('raw_data', {})
                }
            )
            
            db.session.add(pl_statement)
            db.session.commit()
            
            current_app.logger.info(f"P&L statement uploaded for company {company_id}: {filename}")
            
            return jsonify({
                'message': 'P&L statement uploaded successfully',
                'pl_statement_id': pl_statement.id,
                'filename': filename,
                'company_id': company_id,
                'parsed_data': {
                    'revenue': parsed_data.get('revenue', 0.0),
                    'cogs': parsed_data.get('cogs', 0.0),
                    'labor_costs': parsed_data.get('labor_costs', 0.0),
                    'overhead_costs': parsed_data.get('overhead_costs', 0.0),
                    'confidence_score': parsed_data.get('confidence_score', 0.0)
                },
                'validation': validation_result,
                'timestamp': datetime.utcnow().isoformat()
            }), 201
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"P&L upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@upload_bp.route('/financial-data', methods=['POST'])
def upload_financial_data():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        company_id = data.get('company_id')
        if not company_id:
            return jsonify({'error': 'Company ID required'}), 400
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Create P&L statement from JSON data
        pl_statement = PLStatement(
            company_id=company_id,
            revenue=data.get('revenue'),
            cogs=data.get('cogs'),
            labor_costs=data.get('labor_costs'),
            overhead_costs=data.get('overhead_costs'),
            other_costs=data.get('other_costs', {})
        )
        
        db.session.add(pl_statement)
        db.session.commit()
        
        current_app.logger.info(f"Financial data uploaded for company {company_id}")
        
        return jsonify({
            'message': 'Financial data uploaded successfully',
            'pl_statement_id': pl_statement.id,
            'company_id': company_id,
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Financial data upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@upload_bp.route('/upload-pl', methods=['POST'])
def upload_pl():
    """
    Enhanced P&L upload endpoint with intelligent parsing and validation.
    Supports Excel (.xlsx, .xls), CSV, and PDF formats.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        company_id = request.form.get('company_id')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not company_id:
            return jsonify({'error': 'Company ID required'}), 400
        
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
        
        # Trigger webhook for lead capture (placeholder)
        # In production, implement webhook notification here
        
        response_data = {
            'success': True,
            'message': 'P&L statement uploaded and parsed successfully',
            'pl_statement_id': pl_statement.id,
            'company_id': company_id,
            'filename': filename,
            'parsed_data': {
                'revenue': parsed_data.get('revenue', 0.0),
                'cogs': parsed_data.get('cogs', 0.0),
                'labor_costs': parsed_data.get('labor_costs', 0.0),
                'overhead_costs': parsed_data.get('overhead_costs', 0.0),
                'gross_profit': parsed_data.get('revenue', 0.0) - parsed_data.get('cogs', 0.0),
                'total_costs': (parsed_data.get('cogs', 0.0) + 
                              parsed_data.get('labor_costs', 0.0) + 
                              parsed_data.get('overhead_costs', 0.0)),
                'confidence_score': parsed_data.get('confidence_score', 0.0)
            },
            'validation': validation_result,
            'summary': {
                'items_parsed': len(parsed_data.get('raw_data', {}).get('matched_items', [])),
                'categories_found': len([cat for cat in ['revenue', 'cogs', 'labor_costs', 'overhead_costs'] 
                                       if parsed_data.get(cat, 0) > 0])
            },
            'timestamp': datetime.utcnow().isoformat()
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