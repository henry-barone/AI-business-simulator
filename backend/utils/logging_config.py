"""
Structured logging configuration using structlog for better monitoring and debugging.
"""

import logging
import logging.config
import os
import sys
from datetime import datetime
from typing import Dict, Any

import structlog
from flask import has_request_context, request, g


def setup_logging(app=None):
    """
    Configure structured logging for the application.
    
    Args:
        app: Flask application instance
    """
    
    # Configure standard library logging
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = os.getenv('LOG_FORMAT', 'json')  # json or text
    
    # Shared processors for all loggers
    shared_processors = [
        add_request_context,
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]
    
    if log_format.lower() == 'json':
        # JSON logging for production
        shared_processors.extend([
            structlog.processors.JSONRenderer()
        ])
    else:
        # Console logging for development
        shared_processors.extend([
            structlog.processors.CallsiteParameterAdder(
                parameters=[structlog.processors.CallsiteParameter.FILENAME,
                           structlog.processors.CallsiteParameter.LINENO]
            ),
            structlog.dev.ConsoleRenderer(colors=True)
        ])
    
    # Configure structlog
    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level)
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                'format': '%(message)s'
            },
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'json' if log_format.lower() == 'json' else 'standard',
                'stream': sys.stdout
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console'],
                'level': log_level,
                'propagate': False
            },
            'sqlalchemy.engine': {
                'handlers': ['console'],
                'level': 'WARNING',  # Reduce SQL noise
                'propagate': False
            },
            'werkzeug': {
                'handlers': ['console'],
                'level': 'WARNING',  # Reduce HTTP noise
                'propagate': False
            }
        }
    }
    
    # Add file logging for production
    if os.getenv('FLASK_ENV') == 'production':
        log_file = os.getenv('LOG_FILE', '/var/log/ai_business_sim.log')
        logging_config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'json',
            'filename': log_file,
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5
        }
        # Add file handler to all loggers
        for logger_name in logging_config['loggers']:
            logging_config['loggers'][logger_name]['handlers'].append('file')
    
    logging.config.dictConfig(logging_config)
    
    # Set up Flask app logging if provided
    if app:
        app.logger.handlers.clear()
        app.logger.propagate = False
        app.logger.setLevel(getattr(logging, log_level))


def add_request_context(logger, method_name, event_dict):
    """
    Add Flask request context to log entries.
    
    Args:
        logger: Logger instance
        method_name: Log method name
        event_dict: Log event dictionary
        
    Returns:
        Updated event dictionary
    """
    if has_request_context():
        event_dict.update({
            'request_id': getattr(g, 'request_id', None),
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
        })
        
        # Add authenticated user info if available
        if hasattr(g, 'current_company_id'):
            event_dict['company_id'] = g.current_company_id
            
        if hasattr(g, 'current_user_role'):
            event_dict['user_role'] = g.current_user_role
    
    return event_dict


def get_logger(name: str = None):
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (defaults to calling module)
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


class LoggingMiddleware:
    """Middleware to add request ID and timing to all requests."""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger('middleware')
    
    def __call__(self, environ, start_response):
        # Generate unique request ID
        import uuid
        request_id = str(uuid.uuid4())[:8]
        
        def new_start_response(status, response_headers, exc_info=None):
            # Add request ID to response headers
            response_headers.append(('X-Request-ID', request_id))
            return start_response(status, response_headers, exc_info)
        
        # Add request ID to context
        with structlog.contextvars.bound_contextvars(request_id=request_id):
            return self.app(environ, new_start_response)


def log_performance(operation_name: str):
    """
    Decorator to log performance metrics for operations.
    
    Args:
        operation_name: Name of the operation being measured
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger('performance')
            start_time = datetime.utcnow()
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                logger.info(
                    "Operation completed",
                    operation=operation_name,
                    duration_ms=round(duration, 2),
                    success=True
                )
                
                return result
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                logger.error(
                    "Operation failed",
                    operation=operation_name,
                    duration_ms=round(duration, 2),
                    success=False,
                    error=str(e),
                    error_type=type(e).__name__
                )
                
                raise
        
        return wrapper
    return decorator


def log_api_call(logger=None):
    """
    Decorator to log API calls with request/response details.
    
    Args:
        logger: Optional logger instance
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not logger:
                log = get_logger('api')
            else:
                log = logger
            
            start_time = datetime.utcnow()
            
            # Log request start
            log.info(
                "API request started",
                endpoint=func.__name__,
                args=len(args),
                kwargs=list(kwargs.keys())
            )
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Extract status code from Flask response tuple
                status_code = 200
                if isinstance(result, tuple) and len(result) >= 2:
                    status_code = result[1]
                
                log.info(
                    "API request completed",
                    endpoint=func.__name__,
                    duration_ms=round(duration, 2),
                    status_code=status_code,
                    success=status_code < 400
                )
                
                return result
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                log.error(
                    "API request failed",
                    endpoint=func.__name__,
                    duration_ms=round(duration, 2),
                    error=str(e),
                    error_type=type(e).__name__
                )
                
                raise
        
        return wrapper
    return decorator


# Business logic logging helpers
def log_business_event(event_type: str, details: Dict[str, Any], logger=None):
    """
    Log important business events for analytics and monitoring.
    
    Args:
        event_type: Type of business event
        details: Event details dictionary
        logger: Optional logger instance
    """
    if not logger:
        logger = get_logger('business')
    
    logger.info(
        "Business event",
        event_type=event_type,
        **details
    )


def log_security_event(event_type: str, details: Dict[str, Any], level: str = 'warning'):
    """
    Log security-related events for monitoring.
    
    Args:
        event_type: Type of security event
        details: Event details
        level: Log level (info, warning, error)
    """
    logger = get_logger('security')
    
    log_method = getattr(logger, level.lower(), logger.warning)
    log_method(
        "Security event",
        event_type=event_type,
        **details
    )


# Example usage:
#
# # In your Flask app setup:
# from utils.logging_config import setup_logging, LoggingMiddleware
# 
# setup_logging(app)
# app.wsgi_app = LoggingMiddleware(app.wsgi_app)
#
# # In your route handlers:
# @log_api_call()
# @log_performance("create_company")
# def create_company():
#     logger = get_logger(__name__)
#     logger.info("Creating new company", company_name=name)
#     
#     # Business event logging
#     log_business_event("company_created", {
#         "company_id": company.id,
#         "company_name": company.name,
#         "industry": company.industry
#     })
#
# # Security event logging
# log_security_event("authentication_failed", {
#     "ip_address": request.remote_addr,
#     "attempted_company_id": company_id
# }, level="warning")