from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import time

def rate_limit(key_prefix: str, limit: int = None, period: int = None):
    """
    Rate limiting decorator using Redis cache.

    Args:
        key_prefix: Prefix for rate limit key
        limit: Maximum number of requests allowed in the period (defaults to settings)
        period: Time period in seconds (defaults to settings)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Get limits from settings if not provided
            rate_settings = getattr(settings, 'RATE_LIMIT', {}).get('default', {})
            actual_limit = limit or rate_settings.get('LIMIT', 10)
            actual_period = period or rate_settings.get('PERIOD', 60)

            # Generate a unique key for this IP and endpoint
            client_ip = request.META.get('REMOTE_ADDR', 'unknown')
            cache_key = f"ratelimit:{key_prefix}:{client_ip}"

            # Get current requests count
            requests = cache.get(cache_key, [])
            now = time.time()

            # Filter out old requests
            requests = [req for req in requests if req > now - actual_period]

            if len(requests) >= actual_limit:
                return JsonResponse(
                    {"error": "Rate limit exceeded. Please try again later."},
                    status=429
                )

            # Add current request timestamp
            requests.append(now)
            cache.set(cache_key, requests, actual_period)

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
