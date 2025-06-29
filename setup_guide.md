# File: SETUP.md
# Complete setup and deployment guide

# 🤖 AI SEO Auditor - Complete Setup Guide

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning repository)
- OpenAI API key
- OpenRouter API key (optional, for fallback)
- Gmail account with app password (for email reports)
- curl (for health checks)

## 🚀 Quick Start

### 1. Clone or Create Project Structure

Create the following folder structure:

```
seo-auditor/
├── app.py
├── run_production.py
├── requirements.txt
├── .env.example
├── .env
├── README.md
├── SETUP.md
├── Dockerfile
├── docker-compose.yml
├── deploy.sh
├── config/
│   ├── __init__.py
│   └── settings.py
├── models/
│   ├── __init__.py
│   └── database.py
├── services/
│   ├── __init__.py
│   ├── seo_auditor.py
│   ├── ai_service.py
│   ├── web_scraper.py
│   ├── email_service.py
│   ├── report_generator.py
│   └── cache_service.py
├── routes/
│   ├── __init__.py
│   └── api_routes.py
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   ├── logging_config.py
│   └── rate_limiter.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── static/
│   └── index.html
├── deploy/
│   ├── seo-auditor.service
│   ├── logrotate.conf
│   └── nginx.conf
├── reports/      (created automatically)
├── cache/        (created automatically)
└── logs/         (created automatically)
```

### 2. Automated Setup (Recommended)

Use the deployment script for automated setup:

```bash
# Make script executable
chmod +x deploy.sh

# Full deployment
./deploy.sh

# Or specific actions
./deploy.sh deploy    # Full deployment
./deploy.sh dev       # Start development server
./deploy.sh start     # Start production server
./deploy.sh test      # Run tests only
./deploy.sh clean     # Cleanup old files
./deploy.sh health    # Health check
```

### 3. Manual Setup

#### Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` file:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# OpenRouter Configuration (Fallback)
OPENROUTER_API_KEY=sk-or-your-openrouter-key-here

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password
```

#### Create Package Files

```bash
touch config/__init__.py
touch models/__init__.py
touch services/__init__.py
touch routes/__init__.py
touch utils/__init__.py
touch tests/__init__.py
```

## 🚀 Running the Application

### Development Mode

```bash
# Simple development server
python app.py

# Using deployment script
./deploy.sh dev
```

### Production Mode

#### Option 1: Enhanced Production Runner

```bash
# Basic production
python run_production.py

# With custom configuration
python run_production.py --bind 0.0.0.0:8000 --workers 8 --timeout 180

# Available options
python run_production.py --help
```

#### Option 2: Docker (Recommended for Production)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run specific services
docker-compose up seo-auditor redis nginx

# Production with all services
docker-compose up -d
```

#### Option 3: Systemd Service (Linux Servers)

```bash
# Copy service file
sudo cp deploy/seo-auditor.service /etc/systemd/system/

# Edit paths in service file
sudo systemctl edit seo-auditor.service

# Enable and start
sudo systemctl enable seo-auditor
sudo systemctl start seo-auditor

# Check status
sudo systemctl status seo-auditor
```

## ⚙️ Configuration Options

### Production Server Options

```bash
# Command line options
python run_production.py \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --timeout 120 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --log-level info \
  --dry-run  # Show command without running

# Environment variables
export BIND_ADDRESS=0.0.0.0:5000
export WORKERS=4
export TIMEOUT=120
export MAX_REQUESTS=1000
export MAX_REQUESTS_JITTER=100
export LOG_LEVEL=info
```

### Worker Classes

The application automatically detects the best worker class:

- **gevent**: For I/O-bound operations (recommended for SEO auditing)
- **sync**: Fallback for simple synchronous operations

Install gevent for better performance:
```bash
pip install gevent
```

## 🔧 API Keys Setup

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account and navigate to API Keys
3. Create new API key
4. Add to `.env` file: `OPENAI_API_KEY=sk-...`

### OpenRouter API Key (Fallback)
1. Go to [OpenRouter](https://openrouter.ai/)
2. Create account and generate API key
3. Add to `.env` file: `OPENROUTER_API_KEY=sk-or-...`

### Gmail App Password
1. Enable 2FA on Gmail account
2. Google Account → Security → 2-Step Verification → App passwords
3. Generate app password for "Mail"
4. Add to `.env` file: `EMAIL_PASS=your-app-password`

## 🌐 Accessing the Application

### Endpoints

- **Web Interface**: http://localhost:5000
- **API Endpoint**: http://localhost:5000/api/audit
- **Health Check**: http://localhost:5000/health
- **Cache Stats**: http://localhost:5000/api/cache/stats
- **Admin Stats**: http://localhost:5000/admin/stats

### API Usage

```bash
# Run SEO audit
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "email": "user@example.com"}'

# Check health
curl http://localhost:5000/health

# Cache management
curl http://localhost:5000/api/cache/stats
curl -X POST http://localhost:5000/api/cache/clear
curl -X POST http://localhost:5000/api/cache/cleanup
```

## 📊 Monitoring & Logging

### Log Files

```bash
# Application logs
tail -f logs/seo_auditor.log

# Production server logs
tail -f logs/gunicorn.log
tail -f logs/access.log
tail -f logs/error.log

# Production runner logs
tail -f logs/production.log
```

### Health Monitoring

```bash
# Health check
./deploy.sh health

# Service status (systemd)
sudo systemctl status seo-auditor

# Docker logs
docker-compose logs -f seo-auditor
```

### Performance Monitoring

```bash
# Cache statistics
curl http://localhost:5000/api/cache/stats

# Admin statistics
curl http://localhost:5000/admin/stats
```

## 🛡️ Security Features

### Rate Limiting
- **Per IP**: 50 requests/hour
- **Per Email**: 10 requests/hour
- Configurable in `utils/rate_limiter.py`

### Security Headers (Nginx)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: enabled
- Strict-Transport-Security
- Referrer-Policy

### Container Security
- Non-root user execution
- Read-only file system (where applicable)
- Resource limits
- Health checks

## 🧪 Testing

### Run Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test
python -m pytest tests/test_api.py::TestSEOAuditorAPI::test_health_endpoint -v

# With coverage
pip install pytest-cov
python -m pytest tests/ --cov=. --cov-report=html

# Using deployment script
./deploy.sh test
```

### Load Testing

```bash
# Install load testing tool
pip install locust

# Create locustfile.py for load testing
# Run load test
locust -f locustfile.py --host=http://localhost:5000
```

## 🚀 Production Deployment

### Environment Variables for Production

```bash
export FLASK_ENV=production
export WORKERS=4
export BIND_ADDRESS=0.0.0.0:5000
export TIMEOUT=120
export MAX_REQUESTS=1000
export LOG_LEVEL=info
```

### Nginx Reverse Proxy

1. Copy `deploy/nginx.conf` to your Nginx configuration
2. Update SSL certificate paths
3. Adjust server names and upstreams
4. Enable and restart Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/seo-auditor
sudo ln -s /etc/nginx/sites-available/seo-auditor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Log Rotation

The application includes automatic log rotation:

- **Docker**: Built-in log rotation via Docker daemon
- **Systemd**: Use `deploy/logrotate.conf`
- **Manual**: Gunicorn built-in rotation with `--log-file-max-size`

## 🔧 Advanced Configuration

### Custom Worker Configuration

```python
# For CPU-intensive tasks
--worker-class sync --workers 8

# For I/O-intensive tasks (recommended)
--worker-class gevent --workers 4 --worker-connections 1000

# For high-concurrency
--worker-class uvicorn.workers.UvicornWorker --workers 4
```

### Database Optimization

```python
# SQLite optimizations in production
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA temp_store=MEMORY;
```

### Caching Strategy

- **File-based**: Default, suitable for single-server deployments
- **Redis**: For multi-server deployments (included in docker-compose)
- **Memory**: For development and testing

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure all __init__.py files exist
   find . -name "__init__.py" | grep -E "(config|models|services|routes|utils)"
   ```

2. **Permission Errors**
   ```bash
   # Fix directory permissions
   chmod 755 logs cache reports
   chown -R $USER:$USER logs cache reports
   ```

3. **API Key Errors**
   ```bash
   # Verify environment variables
   source .env && echo $OPENAI_API_KEY
   ```

4. **Port Already in Use**
   ```bash
   # Find and kill process
   lsof -ti:5000 | xargs kill -9
   # Or use different port
   python run_production.py --bind 0.0.0.0:8000
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug
python run_production.py --log-level debug

# Development mode with auto-reload
export FLASK_ENV=development
python app.py
```

### Performance Issues

1. **Increase workers**: `--workers 8`
2. **Use gevent**: Automatic with gevent installed
3. **Enable caching**: Redis for multi-server setups
4. **Database optimization**: Enable WAL mode for SQLite

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)

## 🆘 Support

### Getting Help

1. **Check logs**: `tail -f logs/seo_auditor.log`
2. **Verify configuration**: `./deploy.sh health`
3. **Test API keys**: Use environment validation
4. **Network connectivity**: Check firewall and DNS
5. **Resource usage**: Monitor CPU/memory usage

### Debug Information

```bash
# System information
python --version
pip list | grep -E "(flask|gunicorn|requests)"

# Application status
curl -v http://localhost:5000/health

# Log analysis
grep -i error logs/seo_auditor.log | tail -10
```

## 📄 License

MIT License - see LICENSE file for details.