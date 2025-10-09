from django.dispatch import receiver

from django_structlog.signals import bind_extra_request_metadata
import structlog

from tenants.context import get_current_tenant

@receiver(bind_extra_request_metadata)
def remove_ip_address(request, logger, **kwargs):
    structlog.contextvars.bind_contextvars(ip=None)

@receiver(bind_extra_request_metadata)
def remove_request_id(request, logger, **kwargs):
    structlog.contextvars.bind_contextvars(request_id=None)

@receiver(bind_extra_request_metadata)
def bind_tenant_and_subdomain(request, logger, **kwargs):
    current_tenant = get_current_tenant()
    structlog.contextvars.bind_contextvars(tenant=current_tenant.name)
    structlog.contextvars.bind_contextvars(subdomain=current_tenant.subdomain)

