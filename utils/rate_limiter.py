# File: utils/rate_limiter.py
# Rate limiting functionality for API endpoints

import time
from collections import defaultdict, deque
from functools import wraps
from flask import request, jsonify
import hashlib

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(deque)
        self.email_requests = defaultdict(deque)
    
    def is_allowed(self, key, limit=10, window=3600):
        """Check if request is allowed based on rate limit"""
        now = time.time()
        
        # Clean old requests outside the window
        while self.requests[key] and self.requests[key][0] <= now - window:
            self.requests[key].popleft()
        
        # Check if under limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True
        
        return False
    
    def is_email_allowed(self, email, limit=5, window=3600):
        """Check if email-based request is allowed"""
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        now = time.time()
        
        # Clean old requests
        while self.email_requests[email_hash] and self.email_requests[email_hash][0] <= now - window:
            self.email_requests[email_hash].popleft()
        
        # Check if under limit
        if len(self.email_requests[email_hash]) < limit:
            self.email_requests[email_hash].append(now)
            return True
        
        return False
    
    def get_reset_time(self, key, window=3600):
        """Get when the rate limit will reset"""
        if not self.requests[key]:
            return 0
        return int(self.requests[key][0] + window - time.time())

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit=10, window=3600, per='ip'):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if per == 'ip':
                key = request.remote_addr
            elif per == 'email':
                data = request.get_json() or {}
                email = data.get('email')
                if not email:
                    return jsonify({'error': 'Email required for rate limiting'}), 400
                key = hashlib.md5(email.lower().encode()).hexdigest()
            else:
                key = request.remote_addr
            
            if not rate_limiter.is_allowed(key, limit, window):
                reset_time = rate_limiter.get_reset_time(key, window)
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'reset_in': reset_time
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def email_rate_limit(limit=5, window=3600):
    """Email-specific rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json() or {}
            email = data.get('email')
            
            if not email:
                return jsonify({'error': 'Email required'}), 400
            
            if not rate_limiter.is_email_allowed(email, limit, window):
                return jsonify({
                    'error': 'Too many requests from this email address',
                    'message': f'Limit: {limit} requests per {window//60} minutes'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator