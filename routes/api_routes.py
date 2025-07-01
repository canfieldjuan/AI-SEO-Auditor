# File: routes/api_routes.py
# API route definitions with proper error handling to always return JSON

import os
import time
import threading
from typing import Dict  # ADD THIS LINE - THIS IS THE FIX
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
    """Main audit endpoint with comprehensive error handling"""
    start_time = time.time()
    
    # Wrap EVERYTHING in try/except to ensure JSON response
    try:
        # Get and validate request data
        try:
            data = request.get_json() or {}
        except Exception as e:
            return jsonify({'success': False, 'error': 'Invalid JSON in request body'}), 400
        
        url = data.get('url', '').strip()
        email = data.get('email', '').strip()
        
        # Validation
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'}), 400
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        if not is_valid_email(email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Clean and validate URL
        try:
            url = clean_url(url)
            if not is_valid_url(url):
                return jsonify({'success': False, 'error': 'Invalid URL format'}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': f'URL validation error: {str(e)}'}), 400
        
        # Log request (wrapped in try/except)
        try:
            log_audit_request(url, email, request.remote_addr)
        except Exception as e:
            print(f"Logging error (non-fatal): {e}")
        
        # Check cache first
        try:
            cached_result = cache.get(url)
            if cached_result:
                # Still send email with cached results
                try:
                    threading.Thread(
                        target=lambda: auditor.send_cached_report(email, cached_result, url)
                    ).start()
                except:
                    pass  # Don't fail if email threading fails
                
                duration = time.time() - start_time
                
                # Log completion (wrapped)
                try:
                    log_audit_completion(url, email, cached_result.get('score', 0), duration)
                except:
                    pass
                
                return jsonify({
                    **cached_result,
                    'cached': True,
                    'email_sent': True
                })
        except Exception as e:
            print(f"Cache check error (non-fatal): {e}")
            # Continue with fresh audit if cache fails
        
        # Run fresh audit
        try:
            result = auditor.run_full_audit(url, email)
        except Exception as e:
            # Log the error
            try:
                log_error('AUDIT_EXCEPTION', str(e), {'url': url, 'email': email})
            except:
                pass
            
            # Return JSON error response
            return jsonify({
                'success': False, 
                'error': 'Failed to complete audit. Please try again.'
            }), 500
        
        # Check audit result
        if not result.get('success', False):
            # Log the failure
            try:
                log_error('AUDIT_FAILED', result.get('error', 'Unknown error'), {'url': url, 'email': email})
            except:
                pass
            
            return jsonify({
                'success': False,
                'error': result.get('error', 'Audit failed. Please check the URL and try again.')
            }), 400
        
        # Cache successful results (wrapped)
        try:
            cache.set(url, result, ttl=7200)  # Cache for 2 hours
        except Exception as e:
            print(f"Cache set error (non-fatal): {e}")
        
        # Log completion (wrapped)
        try:
            duration = time.time() - start_time
            log_audit_completion(url, email, result.get('score', 0), duration)
        except:
            pass
        
        # Return successful result
        return jsonify(result)
        
    except Exception as e:
        # Catch-all for any unexpected errors
        print(f"Unhandled exception in /api/audit: {e}")
        
        # Try to log the error (but don't fail if logging fails)
        try:
            log_error('AUDIT_UNHANDLED_EXCEPTION', str(e), {
                'url': data.get('url', 'unknown') if 'data' in locals() else 'unknown',
                'email': data.get('email', 'unknown') if 'data' in locals() else 'unknown'
            })
        except:
            pass
        
        # Always return JSON
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

@api_bp.route('/download')
def download_report():
    """Download PDF report"""
    try:
        path = request.args.get('path')
        if not path:
            return jsonify({'success': False, 'error': 'Path parameter required'}), 400
            
        # Security: prevent directory traversal
        if '..' in path or path.startswith('/'):
            return jsonify({'success': False, 'error': 'Invalid path'}), 400
            
        # Construct safe path
        safe_path = os.path.join('reports', os.path.basename(path))
        
        if not os.path.exists(safe_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        return send_file(safe_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Download failed'}), 500

@api_bp.route('/cache/stats')
def cache_stats():
    """Get cache statistics"""
    try:
        stats = cache.get_cache_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to get cache stats'}), 500

@api_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache (admin endpoint)"""
    try:
        # TODO: Add authentication check here
        cleared = cache.clear()
        return jsonify({'success': True, 'cleared_items': cleared})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to clear cache'}), 500

@api_bp.route('/cache/cleanup', methods=['POST'])
def cleanup_cache():
    """Remove expired cache entries"""
    try:
        removed = cache.cleanup_expired()
        return jsonify({'success': True, 'removed_expired': removed})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to cleanup cache'}), 500

# Error handlers for the blueprint
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'error': 'Method not allowed'}), 405

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500