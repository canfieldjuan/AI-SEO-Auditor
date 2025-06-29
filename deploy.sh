# File: deploy.sh
# Automated deployment script for SEO Auditor

#!/bin/bash

# SEO Auditor Deployment Script
set -euo pipefail  # Exit on error, undefined vars, pipe failures

echo "🚀 Starting SEO Auditor deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# Check if virtual environment exists and is activated
check_and_activate_venv() {
    if [ ! -d "venv" ]; then
        warn "Virtual environment not found. Running full deployment first..."
        deploy
        return
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    log "✅ Virtual environment activated"
}

# Check system requirements
check_requirements() {
    log "🔍 Checking system requirements..."
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed."
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 is required but not installed."
    fi
    
    # Check curl for health checks
    if ! command -v curl &> /dev/null; then
        warn "curl not found - health checks will be skipped"
    fi
    
    log "✅ System requirements check passed"
}

# Setup virtual environment
setup_venv() {
    log "📦 Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log "✅ Virtual environment created"
    else
        log "ℹ️  Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    log "✅ pip upgraded"
}

# Install dependencies
install_dependencies() {
    log "📥 Installing dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        error "requirements.txt not found"
    fi
    
    pip install -r requirements.txt
    log "✅ Dependencies installed"
}

# Create directory structure
create_directories() {
    log "📁 Creating directory structure..."
    
    directories=("reports" "cache" "logs" "static" "deploy" "config" "models" "services" "routes" "utils" "tests")
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    # Create __init__.py files for Python packages
    packages=("config" "models" "services" "routes" "utils" "tests")
    for package in "${packages[@]}"; do
        touch "$package/__init__.py"
    done
    
    log "✅ Directory structure created"
}

# Setup environment configuration
setup_environment() {
    log "⚙️  Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            warn ".env file created from template. Please update with your API keys:"
            echo "   - OPENAI_API_KEY"
            echo "   - OPENROUTER_API_KEY" 
            echo "   - EMAIL_USER"
            echo "   - EMAIL_PASS"
        else
            error ".env.example file not found. Cannot create .env file."
        fi
    else
        log "ℹ️  .env file already exists"
    fi
    
    # Validate critical environment variables
    if [ -f ".env" ]; then
        source .env 2>/dev/null || warn "Could not source .env file"
        
        if [ -z "${OPENAI_API_KEY:-}" ] && [ -z "${OPENROUTER_API_KEY:-}" ]; then
            warn "No AI API keys found. At least one of OPENAI_API_KEY or OPENROUTER_API_KEY is required."
        fi
    fi
}

# Run tests
run_tests() {
    log "🧪 Running tests..."
    
    if [ -f "tests/test_api.py" ]; then
        python -m pytest tests/ -v --tb=short
        if [ $? -eq 0 ]; then
            log "✅ All tests passed"
        else
            warn "Some tests failed - check output above"
        fi
    else
        warn "Test files not found - skipping tests"
    fi
}

# Setup file permissions
setup_permissions() {
    log "🔐 Setting up file permissions..."
    
    # Make scripts executable
    chmod +x deploy.sh 2>/dev/null || true
    chmod +x run_production.py 2>/dev/null || true
    
    # Ensure log directories are writable
    chmod 755 logs cache reports 2>/dev/null || true
    
    log "✅ Permissions configured"
}

# Cleanup old files
cleanup() {
    log "🧹 Cleaning up old files..."
    
    # Clean old cache files (older than 7 days)
    find cache/ -name "*.json" -mtime +7 -delete 2>/dev/null || true
    
    # Clean old log files (older than 30 days)
    find logs/ -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    log "✅ Cleanup completed"
}

# Health check function
health_check() {
    if command -v curl &> /dev/null; then
        log "🏥 Performing health check..."
        sleep 5  # Wait for server to start
        
        for i in {1..5}; do
            if curl -f -s http://localhost:5000/health > /dev/null; then
                log "✅ Health check passed"
                return 0
            fi
            warn "Health check attempt $i failed, retrying in 2s..."
            sleep 2
        done
        
        warn "Health check failed after 5 attempts"
        return 1
    else
        warn "curl not available - skipping health check"
        return 0
    fi
}

# Main deployment function
deploy() {
    log "🎯 Starting deployment process..."
    
    check_requirements
    setup_venv
    install_dependencies
    create_directories
    setup_environment
    setup_permissions
    run_tests
    cleanup
    
    log "🎉 Deployment completed successfully!"
    echo ""
    log "📋 Application ready to start:"
    echo "   Development: ./deploy.sh dev"
    echo "   Production:  ./deploy.sh start"
    echo "   Docker:      docker-compose up --build"
    echo ""
    log "📊 Available endpoints:"
    echo "   Web Interface: http://localhost:5000"
    echo "   API Endpoint:  http://localhost:5000/api/audit"
    echo "   Health Check:  http://localhost:5000/health"
    echo "   Cache Stats:   http://localhost:5000/api/cache/stats"
    echo ""
    log "🔍 Monitoring:"
    echo "   Logs:          tail -f logs/seo_auditor.log"
    echo "   Production:    tail -f logs/gunicorn.log"
    echo ""
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "start")
        log "🚀 Starting production server..."
        check_and_activate_venv
        python run_production.py "${@:2}"
        ;;
    "dev")
        log "🚀 Starting development server..."
        check_and_activate_venv
        python app.py
        ;;
    "test")
        log "🧪 Running tests only..."
        check_and_activate_venv
        run_tests
        ;;
    "clean")
        log "🧹 Running cleanup only..."
        cleanup
        ;;
    "health")
        health_check
        ;;
    "setup")
        log "⚙️ Setting up environment only..."
        check_requirements
        setup_venv
        install_dependencies
        create_directories
        setup_environment
        setup_permissions
        log "✅ Setup completed. Run './deploy.sh dev' to start development server."
        ;;
    *)
        echo "Usage: $0 [deploy|start|dev|test|clean|health|setup]"
        echo ""
        echo "Commands:"
        echo "  deploy  - Full deployment (default)"
        echo "  setup   - Setup environment without running tests"
        echo "  start   - Start production server"
        echo "  dev     - Start development server"
        echo "  test    - Run tests only"
        echo "  clean   - Clean up old files"
        echo "  health  - Check application health"
        exit 1
        ;;
esac