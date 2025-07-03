import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from datetime import datetime

from config import config
from models import db
from models.company import Company
from models.simulation import PLStatement, QuestionnaireResponse, Simulation
from models.recommendation import Recommendation

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Configure CORS for Lovable.dev
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints (routes)
    from routes.auth import auth_bp
    from routes.upload import upload_bp
    from routes.questionnaire import questionnaire_bp
    from routes.simulation import simulation_bp
    from routes.recommendations import recommendations_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(questionnaire_bp, url_prefix='/api/questionnaire')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })
    
    # Legacy sandbox endpoint for backwards compatibility
    @app.route('/run_sandbox', methods=['GET'])
    def run_sandbox():
        try:
            from services.simulation_engine import BusinessModel
            
            price = float(request.args.get('price', 30))
            ad_spend = float(request.args.get('ad_spend', 200))
            
            business_model = BusinessModel()
            results = business_model.run_simulation(price, ad_spend)
            
            return jsonify(results), 200
            
        except ValueError as e:
            app.logger.error(f"Invalid parameters in sandbox: {e}")
            return jsonify({'error': 'Invalid parameters'}), 400
        except Exception as e:
            app.logger.error(f"Sandbox simulation error: {e}")
            return jsonify({'error': 'Simulation failed'}), 500
    
    return app

def setup_logging(app):
    if not app.debug and not app.testing:
        # Production logging
        if app.config.get('LOG_FILE'):
            file_handler = logging.FileHandler(app.config['LOG_FILE'])
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
            app.logger.addHandler(file_handler)
        
        app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        app.logger.info('AI Business Simulator startup')

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        app.logger.error(f"HTTP error {e.code}: {e.description}")
        return jsonify({
            'error': e.description,
            'code': e.code,
            'timestamp': datetime.utcnow().isoformat()
        }), e.code
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Resource not found',
            'code': 404,
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        db.session.rollback()
        app.logger.error(f"Unhandled exception: {e}")
        return jsonify({
            'error': 'An unexpected error occurred',
            'code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)