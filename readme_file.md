# File: README.md
# Main project documentation and overview

# AI SEO Auditor

A comprehensive SEO audit tool with AI-powered analysis and OpenRouter fallback support.

## Folder Structure

```
seo-auditor/
├── app.py                      # Main Flask application
├── run_production.py           # Production server with Gunicorn
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # Project documentation
├── deploy.sh                  # Automated deployment script
├── Dockerfile                 # Docker container configuration
├── docker-compose.yml         # Multi-container setup
├── config/
│   ├── __init__.py            # Package initialization
│   └── settings.py            # Configuration settings
├── models/
│   ├── __init__.py            # Package initialization
│   └── database.py            # Database models and operations
├── services/
│   ├── __init__.py            # Package initialization
│   ├── seo_auditor.py         # Main SEO auditor service
│   ├── ai_service.py          # AI service with OpenRouter fallback
│   ├── web_scraper.py         # Web scraping service
│   ├── email_service.py       # Email service
│   ├── report_generator.py    # PDF report generation
│   └── cache_service.py       # Caching service
├── routes/
│   ├── __init__.py            # Package initialization
│   └── api_routes.py          # API route definitions
├── utils/
│   ├── __init__.py            # Package initialization
│   ├── helpers.py             # Helper functions
│   ├── logging_config.py      # Logging configuration
│   └── rate_limiter.py        # Rate limiting
├── tests/
│   ├── __init__.py            # Package initialization
│   └── test_api.py            # API tests
├── static/
│   └── index.html             # Web interface
├── deploy/
│   ├── seo-auditor.service    # Systemd service file
│   ├── nginx.conf             # Nginx configuration
│   └── logrotate.conf         # Log rotation configuration
├── reports/                   # Generated PDF reports (auto-created)
├── cache/                     # Cache files (auto-created)
└── logs/                      # Log files (auto-created)
```

## Features

- **AI-Powered Analysis**: Uses OpenAI GPT-4 for comprehensive SEO analysis
- **OpenRouter Fallback**: Automatically switches to OpenRouter if OpenAI fails
- **Web Scraping**: Extracts comprehensive website data and metadata
- **PDF Reports**: Generates detailed PDF audit reports
- **Email Integration**: Sends audit results via email
- **Database Storage**: Stores audit results in SQLite database
- **RESTful API**: Clean API endpoints for frontend integration

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd seo-auditor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and email settings
   ```

4. **Create necessary directories**
   ```bash
   mkdir reports cache logs
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENROUTER_API_KEY`: Your OpenRouter API key (fallback)
- `EMAIL_HOST`: SMTP server hostname
- `EMAIL_PORT`: SMTP server port
- `EMAIL_USER`: Email username
- `EMAIL_PASS`: Email password or app password

## API Endpoints

### POST /api/audit
Run SEO audit for a website.

**Request Body:**
```json
{
  "url": "https://example.com",
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "score": 85,
  "issues": ["List of issues found"],
  "recommendations": ["List of recommendations"],
  "categories": {
    "technical_seo": 90,
    "content_quality": 80,
    "ai_readiness": 85,
    "voice_search": 75,
    "schema_markup": 60
  },
  "pdf_path": "reports/audit_example_com.pdf",
  "email_sent": true
}
```

### GET /api/download?path=reports/filename.pdf
Download generated PDF report.

### GET /health
Health check endpoint.

## OpenRouter Integration

The application uses OpenRouter as a fallback when OpenAI is unavailable:

1. **Primary**: OpenAI GPT-4 for AI analysis
2. **Fallback**: OpenRouter with the same GPT-4 model
3. **Final Fallback**: Basic rule-based analysis

This ensures high availability and reliability of the audit service.

## Development

The application is structured using Flask blueprints and follows a service-oriented architecture:

- **Services**: Business logic separated into focused services
- **Models**: Database operations and data models
- **Routes**: API endpoint definitions
- **Utils**: Shared utility functions
- **Config**: Centralized configuration management

## Dependencies

- Flask: Web framework
- Flask-CORS: Cross-origin resource sharing
- BeautifulSoup4: HTML parsing
- OpenAI: AI analysis
- Requests: HTTP requests
- ReportLab: PDF generation
- Python-dotenv: Environment variable management

## License

MIT License