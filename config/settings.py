# File: config/settings.py
# Configuration settings and environment variables

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key')

# OpenRouter Configuration (Fallback)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'your-openrouter-api-key')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Email Configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', 'your-email@gmail.com')
EMAIL_PASS = os.getenv('EMAIL_PASS', 'your-app-password')

# Database Configuration
DATABASE_PATH = 'seo_audits.db'

# Report Configuration
REPORTS_DIR = 'reports'