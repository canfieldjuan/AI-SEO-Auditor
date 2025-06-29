# File: utils/logging_config.py
# Logging configuration and audit logging functions

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Setup application logging"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/seo_auditor.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Configure other loggers
    loggers = [
        'services.ai_service',
        'services.web_scraper', 
        'services.email_service',
        'services.report_generator'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
    
    app.logger.info('Logging configured successfully')

def log_audit_request(url, email, user_ip=None):
    """Log audit request"""
    logger = logging.getLogger('audit.request')
    logger.info(f'Audit requested - URL: {url}, Email: {email}, IP: {user_ip}')

def log_audit_completion(url, email, score, duration):
    """Log audit completion"""
    logger = logging.getLogger('audit.completion')
    logger.info(f'Audit completed - URL: {url}, Email: {email}, Score: {score}, Duration: {duration}s')

def log_error(error_type, error_message, context=None):
    """Log errors with context"""
    logger = logging.getLogger('audit.error')
    if context:
        logger.error(f'{error_type}: {error_message} - Context: {context}')
    else:
        logger.error(f'{error_type}: {error_message}')