import os
import redis
from functools import wraps
import json

def get_redis_client():
    rest_url = os.getenv('UPSTASH_REDIS_REST_URL')
    rest_token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
    if not all([rest_url, rest_token]):
        print("Warning: Upstash Redis connection not fully configured.")
        return None
    url = rest_url.replace("https://", "").replace("http://", "").rstrip("/")
    redis_url = f"rediss://:{rest_token}@{url}:6379"
    try:
        r = redis.Redis.from_url(redis_url)
        if r.ping():
            return r
    except Exception as e:
        print(f"Redis connection failed: {e}")
    return None

redis_client = get_redis_client()

def cache_search_results(ttl_seconds=3600):
    """
    Decorator to cache search results in Upstash Redis.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not redis_client:
                return await func(*args, **kwargs)
                
            # Create a simple cache key from function name and kwargs
            # (In production, you'd serialize more robustly)
            query = kwargs.get('query', '')
            cache_key = f"search:{query}"
            
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
                
            result = await func(*args, **kwargs)
            
            # Cache the result
            if result:
                # Need to implement JSON serialization for the SQLAlchemy model results
                # For now, relying on the endpoint returning dicts
                try:
                    redis_client.setex(cache_key, ttl_seconds, json.dumps(result))
                except Exception as e:
                    print(f"Failed to cache result: {e}")
                    
            return result
        return wrapper
    return decorator
