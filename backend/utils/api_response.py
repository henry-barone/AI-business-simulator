"""
Standardized API response utilities for consistent error handling and data formatting.
"""

from flask import jsonify
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
import logging

logger = logging.getLogger(__name__)

def success_response(
    data: Optional[Union[Dict, List, str, int, float]] = None, 
    message: Optional[str] = None, 
    status_code: int = 200,
    meta: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    Create a standardized success response.
    
    Args:
        data: The response data
        message: Optional success message
        status_code: HTTP status code (default: 200)
        meta: Optional metadata (pagination, etc.)
        
    Returns:
        Tuple of (JSON response, status_code)
    """
    response = {
        'success': True,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'status_code': status_code
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
        
    if meta:
        response['meta'] = meta
    
    return jsonify(response), status_code

def error_response(
    error: str, 
    status_code: int = 400, 
    details: Optional[Union[Dict, List, str]] = None,
    error_code: Optional[str] = None
) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        error: Error message
        status_code: HTTP status code (default: 400)
        details: Optional error details or validation errors
        error_code: Optional application-specific error code
        
    Returns:
        Tuple of (JSON response, status_code)
    """
    response = {
        'success': False,
        'error': error,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'status_code': status_code
    }
    
    if details:
        response['details'] = details
        
    if error_code:
        response['error_code'] = error_code
    
    # Log error for monitoring
    log_level = logging.ERROR if status_code >= 500 else logging.WARNING
    logger.log(log_level, f"API Error {status_code}: {error}", extra={
        'status_code': status_code,
        'error_code': error_code,
        'details': details
    })
    
    return jsonify(response), status_code

def validation_error_response(
    validation_errors: Union[Dict[str, List[str]], List[str]], 
    message: str = "Validation failed"
) -> tuple:
    """
    Create a standardized validation error response.
    
    Args:
        validation_errors: Dictionary of field errors or list of general errors
        message: Error message
        
    Returns:
        Tuple of (JSON response, 422)
    """
    return error_response(
        error=message,
        status_code=422,
        details=validation_errors,
        error_code="VALIDATION_ERROR"
    )

def not_found_response(resource: str = "Resource") -> tuple:
    """
    Create a standardized 404 response.
    
    Args:
        resource: Name of the resource that wasn't found
        
    Returns:
        Tuple of (JSON response, 404)
    """
    return error_response(
        error=f"{resource} not found",
        status_code=404,
        error_code="NOT_FOUND"
    )

def unauthorized_response(message: str = "Authentication required") -> tuple:
    """
    Create a standardized 401 response.
    
    Args:
        message: Authentication error message
        
    Returns:
        Tuple of (JSON response, 401)
    """
    return error_response(
        error=message,
        status_code=401,
        error_code="UNAUTHORIZED"
    )

def forbidden_response(message: str = "Access forbidden") -> tuple:
    """
    Create a standardized 403 response.
    
    Args:
        message: Authorization error message
        
    Returns:
        Tuple of (JSON response, 403)
    """
    return error_response(
        error=message,
        status_code=403,
        error_code="FORBIDDEN"
    )

def internal_error_response(message: str = "Internal server error") -> tuple:
    """
    Create a standardized 500 response.
    
    Args:
        message: Error message
        
    Returns:
        Tuple of (JSON response, 500)
    """
    return error_response(
        error=message,
        status_code=500,
        error_code="INTERNAL_ERROR"
    )

def paginated_response(
    data: List[Any],
    page: int,
    per_page: int,
    total: int,
    message: Optional[str] = None
) -> tuple:
    """
    Create a standardized paginated response.
    
    Args:
        data: List of items for current page
        page: Current page number (1-based)
        per_page: Items per page
        total: Total number of items
        message: Optional message
        
    Returns:
        Tuple of (JSON response, 200)
    """
    total_pages = (total + per_page - 1) // per_page
    
    meta = {
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return success_response(data=data, meta=meta, message=message)

class APIException(Exception):
    """
    Custom exception for API errors with structured response data.
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 400, 
        details: Optional[Union[Dict, List, str]] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details
        self.error_code = error_code
    
    def to_response(self) -> tuple:
        """Convert exception to standardized error response."""
        return error_response(
            error=self.message,
            status_code=self.status_code,
            details=self.details,
            error_code=self.error_code
        )

# Common API exceptions
class ValidationError(APIException):
    def __init__(self, message: str = "Validation failed", details=None):
        super().__init__(message, 422, details, "VALIDATION_ERROR")

class NotFoundError(APIException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", 404, error_code="NOT_FOUND")

class UnauthorizedError(APIException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401, error_code="UNAUTHORIZED")

class ForbiddenError(APIException):
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, 403, error_code="FORBIDDEN")

class ConflictError(APIException):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, 409, error_code="CONFLICT")

class InternalError(APIException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, 500, error_code="INTERNAL_ERROR")