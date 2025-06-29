# File: services/cache_service.py
# File-based caching service for audit results

import json
import hashlib
import time
import os
from typing import Optional, Dict, Any

class SimpleCache:
    """Simple file-based cache for audit results"""
    
    def __init__(self, cache_dir='cache', default_ttl=3600):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        # Normalize URL for consistent caching
        url = url.lower().rstrip('/')
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, url: str) -> Optional[Dict[Any, Any]]:
        """Get cached audit result"""
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            # Check if cache is expired
            if time.time() > cached_data.get('expires_at', 0):
                os.remove(cache_path)
                return None
            
            return cached_data.get('data')
            
        except (json.JSONDecodeError, IOError):
            # Remove corrupted cache file
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None
    
    def set(self, url: str, data: Dict[Any, Any], ttl: Optional[int] = None) -> bool:
        """Cache audit result"""
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        if ttl is None:
            ttl = self.default_ttl
        
        cache_data = {
            'data': data,
            'cached_at': time.time(),
            'expires_at': time.time() + ttl,
            'url': url
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            return True
        except IOError:
            return False
    
    def delete(self, url: str) -> bool:
        """Delete cached result"""
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                return True
            except IOError:
                return False
        return True
    
    def clear(self) -> int:
        """Clear all cached results"""
        cleared = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                    cleared += 1
                except IOError:
                    pass
        return cleared
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_files = 0
        total_size = 0
        expired_files = 0
        
        current_time = time.time()
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    total_files += 1
                    
                    # Check if expired
                    with open(file_path, 'r') as f:
                        cached_data = json.load(f)
                    
                    if current_time > cached_data.get('expires_at', 0):
                        expired_files += 1
                        
                except (IOError, json.JSONDecodeError):
                    pass
        
        return {
            'total_cached_items': total_files,
            'total_size_bytes': total_size,
            'expired_items': expired_files,
            'cache_hit_potential': max(0, total_files - expired_files)
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        removed = 0
        current_time = time.time()
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        cached_data = json.load(f)
                    
                    if current_time > cached_data.get('expires_at', 0):
                        os.remove(file_path)
                        removed += 1
                        
                except (IOError, json.JSONDecodeError):
                    # Remove corrupted files too
                    try:
                        os.remove(file_path)
                        removed += 1
                    except IOError:
                        pass
        
        return removed

# Global cache instance
cache = SimpleCache(cache_dir='cache', default_ttl=7200)  # 2 hours default