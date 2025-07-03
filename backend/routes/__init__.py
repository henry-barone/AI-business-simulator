from flask import Blueprint

# Import all route blueprints
from .auth import auth_bp
from .upload import upload_bp
from .questionnaire import questionnaire_bp
from .simulation import simulation_bp
from .recommendations import recommendations_bp