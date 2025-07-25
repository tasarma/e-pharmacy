from django.db import models
from django.db.models.expressions import BaseExpression
from django.conf import settings
from typing import Optional
import uuid

from .context import get_state, get_current_tenant

TENANT_FIELD_NAME = "tenant"


class Tenant(models.Model):
    """
    Represents an organization or customer in a multi-tenant system.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=60, unique=True, db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.subdomain})"


class CurrentTenant(BaseExpression):
    """
    ORM expression that dynamically injects the current tenant ID into SQL queries.
    """

    def as_sql(self, compiler, connection, *args, **kwargs):
        current_tenant = get_current_tenant()

        # Convert the tenant ID to a database-prepared value
        tenant_id = str(current_tenant.id)
        value = self.output_field.get_db_prep_value(tenant_id, connection)

        return "%s", [str(value)]


class TenantManager(models.Manager):
    """
    Custom manager to enforce tenant filtering on all queries automatically.
    """

    def get_queryset(self):
        """
        Automatically filters queries by the current tenant when enabled.
        """
        state = get_state()
        base_queryset = super().get_queryset()

        if not state.get("enabled", True):
            return base_queryset

        # Get the target field type (UUIDField) of the tenant ForeignKey
        field = getattr(self.model, TENANT_FIELD_NAME).field.target_field

        filter_kwargs = {TENANT_FIELD_NAME: CurrentTenant(output_field=field)}

        return base_queryset.filter(**filter_kwargs)

    def bulk_create(self, objs, *args, **kwargs):
        """
        Automatically sets the tenant on each object before bulk creation.
        """
        tenant = get_current_tenant()

        # Set the tenant field on each object before saving
        if tenant:
            for obj in objs:
                setattr(obj, TENANT_FIELD_NAME, tenant)

        return super().bulk_create(objs, *args, **kwargs)


class TenantAwareAbstract(models.Model):
    """
    Abstract base class that ensures objects are saved with the current tenant.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        setattr(self, TENANT_FIELD_NAME, get_current_tenant())
        super().save(*args, **kwargs)

    def get_tenant_instance(self) -> Optional[Tenant]:
        return getattr(self, TENANT_FIELD_NAME, None)


class TenantAwareModel(TenantAwareAbstract):
    """
    Abstract base model that associates each record with a specific tenant.
    """

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="%(class)s_set",  # Creates tenant.product_set, tenant.order_set, etc.
    )

    objects = TenantManager()

    class Meta:
        abstract = True
