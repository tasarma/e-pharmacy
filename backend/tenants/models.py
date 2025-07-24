from django.db import models
from django.conf import settings

import uuid


class Tenant(models.Model):
    """
    Represents a tenant (i.e., an organization or customer) in a multi-tenant system.

    Each tenant has a unique subdomain used for routing, an optional owner (typically a user),
    and basic metadata such as creation date, active status.
    """

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=60, unique=True, db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.subdomain})"


class TenantAwareModel(models.Model):
    """
    Abstract base model that automatically associates any subclass with a specific tenant.

    This is the foundation of our multi-tenant architecture. Any model that inherits
    from TenantAwareModel will automatically be scoped to a tenant, ensuring complete
    data isolation between different tenants.
    """

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="%(class)s_set",  # Creates tenant.product_set, tenant.order_set, etc.
    )

    class Meta:
        abstract = True
