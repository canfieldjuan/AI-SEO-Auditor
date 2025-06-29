# File: run_production.py
# Production server runner for SEO Auditor with Gunicorn

#!/usr/bin/env python3
"""
Production server runner for SEO Auditor
Uses Gunicorn for better performance and reliability
"""
import os
import subprocess
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/production.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

def validate_config(workers, timeout, bind_address):
    """Validate configuration parameters"""
    errors = []
    
    # Validate workers
    try:
        workers_int = int(workers)
        if not (1 <= workers_int <= 32):
            errors.append(f"Workers must be between 1-32, got: {workers}")
    except (ValueError, TypeError):
        errors.append(f"Workers must be an integer, got: {workers}")
    
    # Validate timeout
    try:
        timeout_int = int(timeout)
        if not (30 <= timeout_int <= 600):
            errors.append(f"Timeout must be between 30-600 seconds, got: {timeout}")
    except (ValueError, TypeError):
        errors.append(f"Timeout must be an integer, got: {timeout}")
    
    # Validate bind address format
    if ':' not in bind_address:
        errors.append(f"Bind address must be in format 'host:port', got: {bind_address}")
    else:
        host, port = bind_address.rsplit(':', 1)
        try:
            port_int = int(port)
            if not (1 <= port_int <= 65535):
                errors.append(f"Port must be between 1-65535, got: {port}")
        except ValueError:
            errors.append(f"Port must be an integer, got: {port}")
    
    if errors:
        logger.error("Configuration validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    return int(workers), int(timeout)

def check_gunicorn_availability():
    """Check if Gunicorn is available"""
    try:
        import gunicorn
        logger.info(f"Gunicorn version {gunicorn.__version__} found")
        return True
    except ImportError:
        logger.error("Gunicorn not found. Install with: pip install gunicorn")
        return False

def create_log_directory():
    """Create logs directory with proper error handling"""
    log_path = Path('logs')
    try:
        log_path.mkdir(exist_ok=True)
        # Test write permissions
        test_file = log_path / '.write_test'
        test_file.touch()
        test_file.unlink()
        logger.info(f"Log directory ready: {log_path.absolute()}")
    except PermissionError:
        logger.error(f"Permission denied creating logs directory: {log_path.absolute()}")
        logger.error("Please check directory permissions or run with appropriate privileges")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to create logs directory: {e}")
        sys.exit(1)

def detect_worker_class():
    """Detect best worker class based on app characteristics"""
    # For I/O-bound applications like web scraping and API calls, use gevent
    try:
        import gevent
        logger.info("Gevent available - using async workers for better I/O performance")
        return 'gevent'
    except ImportError:
        logger.info("Gevent not available - using sync workers")
        return 'sync'

def build_gunicorn_command(args):
    """Build Gunicorn command with all options"""
    workers, timeout = validate_config(args.workers, args.timeout, args.bind)
    worker_class = detect_worker_class()
    
    cmd = [
        'gunicorn',
        '--bind', args.bind,
        '--workers', str(workers),
        '--worker-class', worker_class,
        '--timeout', str(timeout),
        '--max-requests', str(args.max_requests),
        '--max-requests-jitter', str(args.max_requests_jitter),
        '--preload',
        '--access-logfile', 'logs/access.log',
        '--error-logfile', 'logs/error.log',
        '--log-file', 'logs/gunicorn.log',
        '--log-level', args.log_level,
        '--capture-output',
        '--enable-stdio-inheritance',
        # Add log rotation
        '--access-logformat', '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
        'app:create_app()'
    ]
    
    # Add worker-specific options
    if worker_class == 'gevent':
        cmd.extend(['--worker-connections', '1000'])
    
    return cmd

def run_production_server(args):
    """Run the application with Gunicorn"""
    logger.info("🚀 Starting SEO Auditor production server...")
    
    # Pre-flight checks
    if not check_gunicorn_availability():
        sys.exit(1)
    
    create_log_directory()
    
    # Build command
    cmd = build_gunicorn_command(args)
    
    # Log configuration
    logger.info(f"📍 Binding to: {args.bind}")
    logger.info(f"👥 Workers: {args.workers}")
    logger.info(f"⏱️ Timeout: {args.timeout}s")
    logger.info(f"🏭 Worker class: {detect_worker_class()}")
    logger.info(f"📝 Logs: logs/access.log, logs/error.log, logs/gunicorn.log")
    logger.info(f"🔧 Max requests per worker: {args.max_requests}")
    logger.info(f"📊 Log level: {args.log_level}")
    logger.info("")
    
    if args.dry_run:
        logger.info("Dry run mode - would execute:")
        logger.info(" ".join(cmd))
        return
    
    try:
        logger.info("Starting Gunicorn server...")
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        logger.info("\n👋 Received shutdown signal, stopping server...")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Gunicorn failed with exit code {e.returncode}")
        logger.error("Check logs/error.log for details")
        sys.exit(e.returncode)
    except FileNotFoundError:
        logger.error("❌ Gunicorn executable not found")
        logger.error("Install with: pip install gunicorn")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Production server runner for SEO Auditor',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--bind', '-b',
        default=os.getenv('BIND_ADDRESS', '0.0.0.0:5000'),
        help='Bind address (host:port)'
    )
    parser.add_argument(
        '--workers', '-w',
        default=os.getenv('WORKERS', '4'),
        help='Number of worker processes'
    )
    parser.add_argument(
        '--timeout', '-t',
        default=os.getenv('TIMEOUT', '120'),
        help='Worker timeout in seconds'
    )
    parser.add_argument(
        '--max-requests',
        default=int(os.getenv('MAX_REQUESTS', '1000')),
        type=int,
        help='Maximum requests per worker before restart'
    )
    parser.add_argument(
        '--max-requests-jitter',
        default=int(os.getenv('MAX_REQUESTS_JITTER', '100')),
        type=int,
        help='Jitter for max-requests to prevent thundering herd'
    )
    parser.add_argument(
        '--log-level',
        default=os.getenv('LOG_LEVEL', 'info'),
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='Logging level'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show command that would be executed without running it'
    )
    
    return parser.parse_args()

if __name__ == '__main__':
    try:
        args = parse_arguments()
        run_production_server(args)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)