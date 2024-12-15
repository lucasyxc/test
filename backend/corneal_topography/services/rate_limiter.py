from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import time

def rate_limit(key_prefix='default', limit=None, period=None):
    """
    Rate limiting decorator that uses Django's cache backend.

    Args:
        key_prefix (str): Prefix for the rate limit key
        limit (int): Number of requests allowed in the period
        period (int): Time period in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Get settings from Django settings or use defaults
            actual_limit = limit or getattr(settings, 'RATE_LIMIT', {}).get(key_prefix, {}).get('LIMIT', 100)
            actual_period = period or getattr(settings, 'RATE_LIMIT', {}).get(key_prefix, {}).get('PERIOD', 3600)

            # Get client IP
            client_ip = request.META.get('REMOTE_ADDR', '')
            cache_key = f"ratelimit:{key_prefix}:{client_ip}"

            # Get current count from cache
            count = cache.get(cache_key, 0)

            # Check if limit is exceeded
            if count >= actual_limit:
                return JsonResponse(
                    {"error": "Rate limit exceeded. Please try again later."},
                    status=429
                )

            # Increment the counter
            if count == 0:
                # First request, set with expiry
                cache.set(cache_key, 1, actual_period)
            else:
                # Increment existing counter
                cache.incr(cache_key)

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
