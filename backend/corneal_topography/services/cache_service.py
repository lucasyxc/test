import logging
from typing import Optional, Any
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class CacheService:
    """Service for handling data caching operations."""

    DEFAULT_TIMEOUT = 3600  # 1 hour default cache timeout

    @staticmethod
    def get_cache_key(prefix: str, identifier: str) -> str:
        """Generate a cache key with prefix."""
        return f"{prefix}:{identifier}"

    def get_patient(self, gkid: str, organization_id: str) -> Optional[Any]:
        """Get patient data from cache."""
        cache_key = self.get_cache_key(f"patient:{organization_id}", gkid)
        return cache.get(cache_key)

    def set_patient(self, gkid: str, organization_id: str, patient_data: Any,
                   timeout: int = DEFAULT_TIMEOUT) -> None:
        """Cache patient data."""
        cache_key = self.get_cache_key(f"patient:{organization_id}", gkid)
        cache.set(cache_key, patient_data, timeout)

    def invalidate_patient(self, gkid: str, organization_id: str) -> None:
        """Remove patient data from cache."""
        cache_key = self.get_cache_key(f"patient:{organization_id}", gkid)
        cache.delete(cache_key)

    def get_examination(self, patient_id: int, date: str) -> Optional[Any]:
        """Get examination data from cache."""
        cache_key = self.get_cache_key("examination", f"{patient_id}:{date}")
        return cache.get(cache_key)

    def set_examination(self, patient_id: int, date: str, exam_data: Any,
                       timeout: int = DEFAULT_TIMEOUT) -> None:
        """Cache examination data."""
        cache_key = self.get_cache_key("examination", f"{patient_id}:{date}")
        cache.set(cache_key, exam_data, timeout)
