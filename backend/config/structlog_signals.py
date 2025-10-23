from django.dispatch import receiver

from django_structlog.signals import bind_extra_request_metadata
import structlog

from tenants.context import get_current_tenant


@receiver(bind_extra_request_metadata)
def remove_ip_address(request, logger, **kwargs):
    structlog.contextvars.bind_contextvars(ip=None)


@receiver(bind_extra_request_metadata)
def bind_subdomain(request, logger, **kwargs):
    if not request.path.startswith("/admin/"):
        try:
            current_tenant = get_current_tenant()
            structlog.contextvars.bind_contextvars(subdomain=current_tenant.subdomain)
        except Exception as e:
            logger.warning("failed_to_bind_tenant_context", error=str(e))
