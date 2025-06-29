# File: config/settings.py
# Configuration settings for the SEO Auditor application

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App Settings
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Database
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/seo_auditor.db')

# Directories
REPORTS_DIR = os.getenv('REPORTS_DIR', 'reports')
CACHE_DIR = os.getenv('CACHE_DIR', 'cache')
LOGS_DIR = os.getenv('LOGS_DIR', 'logs')
STATIC_DIR = os.getenv('STATIC_DIR', 'static')

# Email Configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', '')  # Your email
EMAIL_PASS = os.getenv('EMAIL_PASS', '')  # Your app password

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')

# Rate Limiting
RATE_LIMIT_PER_IP = int(os.getenv('RATE_LIMIT_PER_IP', '50'))
RATE_LIMIT_PER_EMAIL = int(os.getenv('RATE_LIMIT_PER_EMAIL', '10'))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # 1 hour

# Cache Settings
CACHE_TTL = int(os.getenv('CACHE_TTL', '7200'))  # 2 hours

# Create required directories
for directory in [REPORTS_DIR, CACHE_DIR, LOGS_DIR, STATIC_DIR, os.path.dirname(DATABASE_PATH)]:
    os.makedirs(directory, exist_ok=True)