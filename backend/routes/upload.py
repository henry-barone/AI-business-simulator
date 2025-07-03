from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from models import db
from models.company import Company
from models.simulation import PLStatement

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
            
            # Placeholder for file parsing logic
            # In production, implement actual P&L parsing from the file
            pl_statement = PLStatement(
                company_id=company_id,
                revenue=0.0,  # Parse from file
                cogs=0.0,     # Parse from file
                labor_costs=0.0,  # Parse from file
                overhead_costs=0.0,  # Parse from file
                other_costs={'filename': filename, 'filepath': filepath}
            )
            
            db.session.add(pl_statement)
            db.session.commit()
            
            current_app.logger.info(f"P&L statement uploaded for company {company_id}: {filename}")
            
            return jsonify({
                'message': 'P&L statement uploaded successfully',
                'pl_statement_id': pl_statement.id,
                'filename': filename,
                'company_id': company_id,
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