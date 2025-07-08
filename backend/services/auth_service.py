"""
JWT Authentication service for secure API access.
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app
from typing import Dict, Any, Optional, Callable
import logging

from utils.api_response import unauthorized_response, forbidden_response
from models.company import Company

logger = logging.getLogger(__name__)

class AuthService:
    """JWT Authentication and authorization service."""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.token_expiry_hours = int(os.getenv('JWT_EXPIRY_HOURS', '24'))
        
        if self.secret_key == 'dev-secret-key-change-in-production' and os.getenv('FLASK_ENV') == 'production':
            logger.error("JWT_SECRET_KEY not set in production environment!")
    
    def generate_token(self, company_id: int, user_role: str = 'user') -> str:
        """
        Generate JWT token for authenticated company.
        
        Args:
            company_id: Company ID
            user_role: User role (user, admin, etc.)
            
        Returns:
            JWT token string
        """
        payload = {
            'company_id': company_id,
            'role': user_role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"Token generated for company {company_id}")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def get_token_from_request(self) -> Optional[str]:
        """
        Extract JWT token from request headers.
        
        Returns:
            Token string or None if not found
        """
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        return None
    
    def authenticate_company(self, company_id: int, password: str = None) -> bool:
        """
        Authenticate company (simplified for demo - in production use proper password hashing).
        
        Args:
            company_id: Company ID
            password: Password (optional for demo)
            
        Returns:
            True if authenticated
        """
        # For demo purposes, we'll just check if company exists
        # In production, implement proper password verification
        company = Company.query.get(company_id)
        return company is not None

def jwt_required(roles: Optional[list] = None):
    """
    Decorator to require JWT authentication for routes.
    
    Args:
        roles: Optional list of required roles
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_service = AuthService()
            
            # Get token from request
            token = auth_service.get_token_from_request()
            if not token:
                return unauthorized_response("Authentication token required")
            
            # Verify token
            payload = auth_service.verify_token(token)
            if not payload:
                return unauthorized_response("Invalid or expired token")
            
            # Check role if specified
            if roles:
                user_role = payload.get('role', 'user')
                if user_role not in roles:
                    return forbidden_response("Insufficient permissions")
            
            # Add company info to kwargs
            kwargs['current_company_id'] = payload['company_id']
            kwargs['current_user_role'] = payload.get('role', 'user')
            kwargs['token_payload'] = payload
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def optional_jwt():
    """
    Decorator for optional JWT authentication.
    Adds company info if token is present and valid, but doesn't require it.
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_service = AuthService()
            
            # Try to get token
            token = auth_service.get_token_from_request()
            if token:
                payload = auth_service.verify_token(token)
                if payload:
                    kwargs['current_company_id'] = payload['company_id']
                    kwargs['current_user_role'] = payload.get('role', 'user')
                    kwargs['token_payload'] = payload
            
            # Set defaults if no valid token
            if 'current_company_id' not in kwargs:
                kwargs['current_company_id'] = None
                kwargs['current_user_role'] = None
                kwargs['token_payload'] = None
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def admin_required():
    """Decorator to require admin role."""
    return jwt_required(roles=['admin'])

def same_company_required():
    """
    Decorator to ensure user can only access their own company's data.
    Must be used after jwt_required.
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_company_id = kwargs.get('current_company_id')
            
            # Check if company_id is in URL parameters
            requested_company_id = kwargs.get('company_id')
            if requested_company_id and current_company_id != requested_company_id:
                return forbidden_response("Access denied to other company's data")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

class RateLimiter:
    """Simple in-memory rate limiter (use Redis in production)."""
    
    def __init__(self):
        self.requests = {}  # In production, use Redis
        self.enabled = os.getenv('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    
    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Unique identifier (IP, user ID, etc.)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if request is allowed
        """
        if not self.enabled:
            return True
        
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old requests
        if key in self.requests:
            self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        else:
            self.requests[key] = []
        
        # Check limit
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

def rate_limit(max_requests: int = 100, window_seconds: int = 3600, per: str = 'ip'):
    """
    Rate limiting decorator.
    
    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        per: Rate limit per 'ip' or 'user'
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = RateLimiter()
            
            # Determine rate limit key
            if per == 'user' and 'current_company_id' in kwargs:
                key = f"user_{kwargs['current_company_id']}"
            else:
                key = f"ip_{request.remote_addr}"
            
            if not limiter.is_allowed(key, max_requests, window_seconds):
                return error_response(
                    "Rate limit exceeded",
                    status_code=429,
                    error_code="RATE_LIMIT_EXCEEDED"
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Example usage patterns:
#
# @app.route('/protected')
# @jwt_required()
# def protected_route(current_company_id, current_user_role, token_payload):
#     return f"Hello company {current_company_id}"
#
# @app.route('/admin')
# @admin_required()
# def admin_route(current_company_id, current_user_role, token_payload):
#     return "Admin only"
#
# @app.route('/companies/<int:company_id>/data')
# @jwt_required()
# @same_company_required()
# def company_data(company_id, current_company_id, current_user_role, token_payload):
#     return f"Data for company {company_id}"
#
# @app.route('/limited')
# @rate_limit(max_requests=10, window_seconds=60)
# def limited_route():
#     return "Rate limited endpoint"