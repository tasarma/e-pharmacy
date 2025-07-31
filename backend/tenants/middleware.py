from django.http import HttpRequest, HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from typing import Optional, Callable

from .models import Tenant
from .context import set_tenant_context, tenant_context_disabled


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

        if request.path.startswith("/admin/"):
            with tenant_context_disabled():
                return self.get_response(request)

        # TODO: IN PRODUCTION use host = request.get_host()
        host = request.META.get("HTTP_HOST", "")
        subdomain = self.get_subdomain(host)
        tenant = self.get_tenant(subdomain) if subdomain else None

        if tenant is None:
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

        # Remove port ('example.com:8000' -> 'example.com')
        host = host.split(":")[0]
        parts = host.split(".")

        return parts[0] if len(parts) >= 3 else None

    def get_tenant(self, subdomain: str) -> Optional[Tenant]:
        """
        Get Tenant using subdomain.
        """
        # TODO:  Cashe tenant lookup
        # TODO:  Get tenant from session for logged in users and from request for anonymous users

        try:
            return Tenant.objects.get(subdomain=subdomain, active=True)
        except ObjectDoesNotExist:
            return None
