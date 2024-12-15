from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)

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

            # Get client identifier
            if getattr(settings, 'TESTING', False):
                client_id = 'test_client'
            else:
                client_id = request.META.get('REMOTE_ADDR', 'default')

            cache_key = f"ratelimit:{key_prefix}:{client_id}"

            # Get current count and timestamp from cache
            cache_data = cache.get(cache_key)
            current_time = int(time.time())

            if cache_data:
                count, start_time = cache_data
                # Reset if period has expired
                if current_time - start_time >= actual_period:
                    logger.debug(f"Rate limit period expired for {cache_key}")
                    count = 0
                    start_time = current_time
            else:
                count = 0
                start_time = current_time
                logger.debug(f"New rate limit entry for {cache_key}")

            logger.debug(f"Rate limit check - Key: {cache_key}, Count: {count}, Limit: {actual_limit}")

            # Check if limit is exceeded
            if count >= actual_limit:
                logger.warning(f"Rate limit exceeded for {cache_key} - Count: {count}, Limit: {actual_limit}")
                return JsonResponse(
                    {"error": "Rate limit exceeded. Please try again later."},
                    status=429
                )

            # Increment the counter and update timestamp
            count += 1
            cache.set(cache_key, (count, start_time), actual_period)
            logger.debug(f"Updated rate limit - Key: {cache_key}, New Count: {count}")

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
