from django.http import HttpRequest, HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from typing import Optional, Callable

from .models import Tenant
from .context import set_tenant_context


class TenantAwareMiddleware:
    """
    Middleware to automatically detect tenant from subdomain and set tenant context.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # TODO: IN PRODUCTION use host = request.get_host() which is more safer
        host = request.META.get("HTTP_HOST", "")
        subdomain = self.get_subdomain(host)

        if subdomain is None:
            return self.get_response(request)

        try:
            tenant = Tenant.objects.get(subdomain=subdomain, active=True)
        except ObjectDoesNotExist:
            raise Http404(f"Tenant with subdomain '{subdomain}' not found")

        with set_tenant_context(tenant=tenant):
            response = self.get_response(request)

        return response

    def get_subdomain(self, host: str) -> Optional[str]:
        """
        Extract subdomain from host header.
        """
        if not host:
            return None

        # Remove port (e.g., 'example.com:8000' -> 'example.com')
        host = host.split(":")[0]
        parts = host.split(".")

        if len(parts) < 3:
            return None

        return parts[0]
