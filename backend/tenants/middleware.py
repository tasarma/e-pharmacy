from django.http import HttpRequest, HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from typing import Optional, Callable
import structlog
import re

from .models import Tenant
from .context import set_tenant_context, tenant_context_disabled

logger = structlog.get_logger(__name__)

SUBDOMAIN_PATTERN = re.compile(r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$', re.IGNORECASE)
BYPASS_PATHS = ("/admin/", "/health/", "/metrics/")
TENANT_CACHE_TIMEOUT = 300  # 5 minutes


class TenantAwareMiddleware:
    """
    Middleware to automatically detect tenant from subdomain and set tenant context.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # TODO: Activate in production
        # if not request.user.is_authenticated:
        #     return self.get_response(request)

        # Bypass tenant enforcement for specific paths
        if any(request.path.startswith(path) for path in BYPASS_PATHS):
            with tenant_context_disabled():
                return self.get_response(request)

        try:
            # TODO: IN PRODUCTION use host = request.get_host()
            # host = request.get_host()
            host = request.META.get("HTTP_HOST", "")
        except Exception as e:
            logger.warning("invalid_host_header", error=str(e))
            raise Http404("Invalid host")

        subdomain = self.get_subdomain(host)
        if not subdomain:
            logger.warning("no_subdomain_found", host=host)
            raise Http404("Tenant not found")

        tenant = self.get_tenant(subdomain)

        if tenant is None:
            logger.warning("tenant_not_found", subdomain=subdomain)
            raise Http404("Tenant not found")

        with set_tenant_context(tenant=tenant):
            response = self.get_response(request)

        return response

    def get_subdomain(self, host: str) -> Optional[str]:
        """Extract and validate subdomain from host header."""
        if not host:
            return None

        # Remove port ('example.com:8000' -> 'example.com')
        host = host.split(":")[0].lower()
        parts = host.split(".")

        if len(parts) < 3:
            return None
        
        subdomain = parts[0]
        
        if not SUBDOMAIN_PATTERN.match(subdomain):
            logger.warning("invalid_subdomain_format", subdomain=subdomain)
            return None
        
        return subdomain

    def get_tenant(self, subdomain: str) -> Optional[Tenant]:
        """Get tenant by subdomain with caching."""
        cache_key = f"tenant:subdomain:{subdomain}"
        cached = cache.get(cache_key)

        if cached is not None:
            return None if cached == "NOT_FOUND" else cached

        try:
            tenant = Tenant.objects.select_related().get(
                subdomain=subdomain, 
                active=True
            )
            cache.set(cache_key, tenant, timeout=TENANT_CACHE_TIMEOUT)
            logger.info("tenant_loaded", tenant_id=str(tenant.id))
            return tenant
            
        except ObjectDoesNotExist:
            # Cache negative results to prevent DB hammering
            cache.set(cache_key, "NOT_FOUND", timeout=60)
            return None
