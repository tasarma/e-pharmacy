from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.expressions import BaseExpression
from django.db.models.constraints import UniqueConstraint
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


class UniqueTenantConstraint(UniqueConstraint):
    def __init__(self, *expressions, fields=(), **kwargs):
        if TENANT_FIELD_NAME not in fields:
            fields = (TENANT_FIELD_NAME,) + tuple(fields)

        super().__init__(*expressions, fields=fields, **kwargs)

    def validate(self, model, instance, exclude=None, *args, **kwargs):
        if exclude and TENANT_FIELD_NAME in exclude:
            exclude = [field for field in exclude if field != TENANT_FIELD_NAME]

        setattr(instance, TENANT_FIELD_NAME, get_current_tenant())

        try:
            super().validate(model, instance, exclude, *args, **kwargs)
        except ValidationError as e:
            use_default_message = (
                self.violation_error_message == self.default_violation_error_message
            )
            if use_default_message:
                fields = set(self.fields) ^ {TENANT_FIELD_NAME}
                error = instance.unique_error_message(model, list(fields))
                self.violation_error_message = error.message % error.params

            raise ValidationError(self.violation_error_message) from e
