# File: routes/api_routes.py
# API route definitions with rate limiting and caching

import os
import time
import threading
from flask import Blueprint, request, jsonify, send_file
from services.seo_auditor import SEOAuditor
from services.cache_service import cache
from utils.helpers import clean_url, is_valid_email, is_valid_url
from utils.rate_limiter import rate_limit, email_rate_limit
from utils.logging_config import log_audit_request, log_audit_completion, log_error

api_bp = Blueprint('api', __name__)
auditor = SEOAuditor()

@api_bp.route('/audit', methods=['POST'])
@rate_limit(limit=50, window=3600, per='ip')  # 50 requests per hour per IP
@email_rate_limit(limit=10, window=3600)      # 10 requests per hour per email
def run_audit():
    """Main audit endpoint with caching and rate limiting"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        url = data.get('url')
        email = data.get('email')
        
        # Validation
        if not url or not email:
            return jsonify({'success': False, 'error': 'URL and email are required'}), 400
        
        if not is_valid_email(email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Clean URL
        url = clean_url(url)
        
        if not is_valid_url(url):
            return jsonify({'success': False, 'error': 'Invalid URL format'}), 400
        
        # Log request
        log_audit_request(url, email, request.remote_addr)
        
        # Check cache first
        cached_result = cache.get(url)
        if cached_result:
            # Still send email with cached results
            threading.Thread(
                target=lambda: auditor.send_cached_report(email, cached_result, url)
            ).start()
            
            duration = time.time() - start_time
            log_audit_completion(url, email, cached_result.get('score', 0), duration)
            
            return jsonify({
                **cached_result,
                'cached': True,
                'email_sent': True
            })
        
        # Run fresh audit
        result = auditor.run_full_audit(url, email)
        
        if not result['success']:
            log_error('AUDIT_FAILED', result.get('error', 'Unknown error'), {'url': url, 'email': email})
            return jsonify(result), 400
        
        # Cache successful results
        cache.set(url, result, ttl=7200)  # Cache for 2 hours
        
        # Log completion
        duration = time.time() - start_time
        log_audit_completion(url, email, result.get('score', 0), duration)
        
        return jsonify(result)
        
    except Exception as e:
        log_error('AUDIT_EXCEPTION', str(e), {'url': url, 'email': email})
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/download')
def download_report():
    """Download PDF report"""
    path = request.args.get('path')
    if not path or not os.path.exists(path):
        return "File not found", 404
    
    return send_file(path, as_attachment=True)

@api_bp.route('/cache/stats')
def cache_stats():
    """Get cache statistics"""
    try:
        stats = cache.get_cache_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache (admin endpoint)"""
    try:
        cleared = cache.clear()
        return jsonify({'cleared_items': cleared})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/cache/cleanup', methods=['POST'])
def cleanup_cache():
    """Remove expired cache entries"""
    try:
        removed = cache.cleanup_expired()
        return jsonify({'removed_expired': removed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500