"""
Request validation utilities using Cerberus for input sanitization and validation.
"""

from cerberus import Validator
from functools import wraps
from flask import request
from typing import Dict, Any, List, Optional, Callable
import mimetypes
import os
import re
from utils.api_response import validation_error_response

class CustomValidator(Validator):
    """Extended Cerberus validator with custom rules for manufacturing data."""
    
    def _validate_is_positive(self, is_positive, field, value):
        """Validate that a numeric value is positive."""
        if is_positive and value is not None and value <= 0:
            self._error(field, "Must be a positive number")
    
    def _validate_is_email(self, is_email, field, value):
        """Validate email format."""
        if is_email and value:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, value):
                self._error(field, "Must be a valid email address")
    
    def _validate_is_url(self, is_url, field, value):
        """Validate URL format."""
        if is_url and value:
            url_regex = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
            if not re.match(url_regex, value):
                self._error(field, "Must be a valid URL")
    
    def _validate_file_type(self, allowed_types, field, value):
        """Validate file type based on extension and MIME type."""
        if value and allowed_types:
            # Check file extension
            ext = os.path.splitext(value.filename)[1].lower() if hasattr(value, 'filename') else ''
            
            # Map common extensions to types
            type_extensions = {
                'excel': ['.xlsx', '.xls'],
                'pdf': ['.pdf'],
                'csv': ['.csv'],
                'image': ['.jpg', '.jpeg', '.png', '.gif'],
                'document': ['.doc', '.docx', '.pdf', '.txt']
            }
            
            valid_extensions = []
            for file_type in allowed_types:
                valid_extensions.extend(type_extensions.get(file_type, []))
            
            if ext not in valid_extensions:
                self._error(field, f"File type not allowed. Allowed types: {', '.join(allowed_types)}")

# Common validation schemas
COMPANY_SCHEMA = {
    'name': {
        'type': 'string',
        'required': True,
        'minlength': 2,
        'maxlength': 100,
        'regex': r'^[a-zA-Z0-9\s\-\.\&]+$'
    },
    'industry': {
        'type': 'string',
        'required': True,
        'allowed': ['Manufacturing', 'Automotive', 'Electronics', 'Food & Beverage', 
                   'Textiles', 'Chemicals', 'Pharmaceuticals', 'Other']
    },
    'employee_count': {
        'type': 'string',
        'required': False,
        'allowed': ['1-10', '11-25', '26-50', '51-100', '101-200', '201-500', '500+']
    },
    'annual_revenue': {
        'type': 'float',
        'required': False,
        'is_positive': True,
        'max': 1000000000  # 1 billion cap
    }
}

QUESTIONNAIRE_RESPONSE_SCHEMA = {
    'session_id': {
        'type': 'string',
        'required': True,
        'regex': r'^[a-zA-Z0-9\-]+$'
    },
    'question_id': {
        'type': 'integer',
        'required': True,
        'min': 1
    },
    'answer': {
        'type': 'string',
        'required': True,
        'maxlength': 5000
    },
    'answer_type': {
        'type': 'string',
        'required': True,
        'allowed': ['text', 'multiple_choice', 'rating', 'boolean']
    }
}

SIMULATION_PARAMS_SCHEMA = {
    'automation_levels': {
        'type': 'dict',
        'required': False,
        'schema': {
            'labor': {'type': 'float', 'min': 0.0, 'max': 1.0},
            'quality': {'type': 'float', 'min': 0.0, 'max': 1.0},
            'inventory': {'type': 'float', 'min': 0.0, 'max': 1.0},
            'service': {'type': 'float', 'min': 0.0, 'max': 1.0}
        }
    },
    'projection_months': {
        'type': 'integer',
        'required': False,
        'min': 6,
        'max': 60
    },
    'production_volume': {
        'type': 'string',
        'required': False,
        'allowed': ['<100 units/day', '100-1000 units/day', '1000-10000 units/day', '10000+ units/day']
    }
}

FILE_UPLOAD_SCHEMA = {
    'file': {
        'required': True,
        'file_type': ['excel', 'pdf', 'csv']
    },
    'file_type': {
        'type': 'string',
        'required': False,
        'allowed': ['pl_statement', 'financial_report', 'other']
    }
}

def validate_request(schema: Dict[str, Any], location: str = 'json'):
    """
    Decorator to validate request data against a schema.
    
    Args:
        schema: Cerberus validation schema
        location: Where to get data from ('json', 'form', 'args', 'files')
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            validator = CustomValidator(schema)
            
            # Get data based on location
            if location == 'json':
                if not request.is_json:
                    return validation_error_response(
                        ["Request must be JSON"],
                        "Invalid content type"
                    )
                data = request.get_json() or {}
            elif location == 'form':
                data = request.form.to_dict()
            elif location == 'args':
                data = request.args.to_dict()
            elif location == 'files':
                data = {}
                for key in request.files:
                    data[key] = request.files[key]
            else:
                data = {}
            
            # Validate data
            if not validator.validate(data):
                return validation_error_response(
                    validator.errors,
                    "Validation failed"
                )
            
            # Add validated data to kwargs
            kwargs['validated_data'] = validator.document
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input to prevent XSS and injection attacks.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # Remove or escape potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', value)
    
    # Limit length
    sanitized = sanitized[:max_length]
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized

def validate_file_upload(file, allowed_types: List[str], max_size_mb: int = 10) -> Optional[str]:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file object
        allowed_types: List of allowed file types
        max_size_mb: Maximum file size in MB
        
    Returns:
        Error message if validation fails, None if valid
    """
    if not file or not file.filename:
        return "No file provided"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > max_size_mb * 1024 * 1024:
        return f"File too large. Maximum size: {max_size_mb}MB"
    
    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    
    type_extensions = {
        'excel': ['.xlsx', '.xls'],
        'pdf': ['.pdf'],
        'csv': ['.csv'],
        'image': ['.jpg', '.jpeg', '.png', '.gif']
    }
    
    valid_extensions = []
    for file_type in allowed_types:
        valid_extensions.extend(type_extensions.get(file_type, []))
    
    if ext not in valid_extensions:
        return f"Invalid file type. Allowed: {', '.join(allowed_types)}"
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type:
        dangerous_types = [
            'application/x-executable',
            'application/x-msdownload',
            'application/x-msdos-program'
        ]
        if mime_type in dangerous_types:
            return "File type not allowed for security reasons"
    
    return None

def validate_financial_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate financial data for logical consistency.
    
    Args:
        data: Financial data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    revenue = data.get('revenue', 0)
    cogs = data.get('cogs', 0)
    labor_costs = data.get('labor_costs', 0)
    overhead_costs = data.get('overhead_costs', 0)
    
    # Basic validation
    if revenue <= 0:
        errors.append("Revenue must be positive")
    
    if cogs < 0 or labor_costs < 0 or overhead_costs < 0:
        errors.append("Costs cannot be negative")
    
    # Logical validation
    total_costs = cogs + labor_costs + overhead_costs
    if total_costs > revenue * 1.5:  # Allow some flexibility
        errors.append("Total costs seem unusually high compared to revenue")
    
    if labor_costs > revenue * 0.8:
        errors.append("Labor costs seem unusually high")
    
    if cogs > revenue * 0.9:
        errors.append("Cost of goods sold seems unusually high")
    
    return errors

def validate_automation_levels(levels: Dict[str, float]) -> List[str]:
    """
    Validate automation level parameters.
    
    Args:
        levels: Dictionary of automation levels
        
    Returns:
        List of validation errors
    """
    errors = []
    required_keys = ['labor', 'quality', 'inventory', 'service']
    
    for key in required_keys:
        if key not in levels:
            errors.append(f"Missing automation level for {key}")
        else:
            value = levels[key]
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                errors.append(f"Automation level for {key} must be between 0 and 1")
    
    return errors