from django.core.cache import cache
from datetime import timedelta
import structlog

logger = structlog.get_logger(__name__)

def track_onboarding_attempt(ip_address: str, success: bool) -> None:
    """Track failed onboarding attempts for fraud detection."""
    key = f"onboarding_failures:{ip_address}"
    
    if success:
        cache.delete(key)
    else:
        failures = cache.get(key, 0) + 1
        cache.set(key, failures, timeout=3600)  # 1 hour
        
        if failures >= 5:
            logger.warning(
                "suspicious_onboarding_activity",
                ip=ip_address,
                failure_count=failures
            )
            # TODO: Send alert to monitoring system
