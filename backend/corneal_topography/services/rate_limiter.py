from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse
import time

def rate_limit(key_prefix: str, limit: int = 10, period: int = 60):
    """
    Rate limiting decorator using Redis cache.

    Args:
        key_prefix: Prefix for rate limit key
        limit: Maximum number of requests allowed in the period
        period: Time period in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Generate a unique key for this IP and endpoint
            client_ip = request.META.get('REMOTE_ADDR')
            cache_key = f"ratelimit:{key_prefix}:{client_ip}"

            # Get current requests count
            requests = cache.get(cache_key, [])
            now = time.time()

            # Filter out old requests
            requests = [req for req in requests if req > now - period]

            if len(requests) >= limit:
                return HttpResponse(
                    "Rate limit exceeded. Please try again later.",
                    status=429
                )

            # Add current request timestamp
            requests.append(now)
            cache.set(cache_key, requests, period)

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
