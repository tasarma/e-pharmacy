from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.expressions import BaseExpression
from django.db.models.constraints import UniqueConstraint
from typing import Optional
import uuid
import re
import structlog

from .context import get_state, get_current_tenant

logger = structlog.get_logger(__name__)

TENANT_FIELD_NAME = "tenant"
RESERVED_SUBDOMAINS = frozenset({'www', 'api', 'admin', 'app', 'mail', 'ftp', 'localhost', 'static', 'media'})


class Tenant(models.Model):
    """Organization or customer in multi-tenant system."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=60, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['subdomain', 'active']),
        ]

    def clean(self):
        if not re.match(r'^[a-z0-9]([a-z0-9-]{0,58}[a-z0-9])?$', self.subdomain):
            raise ValidationError("Subdomain must be lowercase alphanumeric with hyphens")
        
        if self.subdomain.lower() in RESERVED_SUBDOMAINS:
            raise ValidationError(f"Subdomain '{self.subdomain}' is reserved")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.subdomain})"
    
    def __repr__(self) -> str:
        return f"<Tenant id={self.id} subdomain={self.subdomain} active={self.active}>"


class CurrentTenant(BaseExpression):
    """ORM expression that injects current tenant ID into queries."""

    def as_sql(self, compiler, connection, *args, **kwargs):
        current_tenant = get_current_tenant()

        # Convert the tenant ID to a database-prepared value
        # tenant_id = str(current_tenant.id)
        value = self.output_field.get_db_prep_value(current_tenant.id, connection)
        return "%s", [value]


class TenantManager(models.Manager):
    """Custom manager to enforce tenant filtering on all queries automatically."""

    def get_queryset(self):
        """Automatically filters queries by the current tenant when enabled."""
        state = get_state()
        base_queryset = super().get_queryset()

        if not state.get("enabled", True):
            return base_queryset

        # Get the target field type (UUIDField) of the tenant ForeignKey
        field = getattr(self.model, TENANT_FIELD_NAME).field.target_field

        filter_kwargs = {TENANT_FIELD_NAME: CurrentTenant(output_field=field)}

        return base_queryset.filter(**filter_kwargs)

    def bulk_create(self, objs, *args, **kwargs):
        """Automatically sets the tenant on each object before bulk creation."""
        tenant = get_current_tenant()

        # Set the tenant field on each object before saving
        if tenant:
            for obj in objs:
                existing_tenant = getattr(obj, TENANT_FIELD_NAME, None)
                if existing_tenant and existing_tenant.id != tenant.id:
                    raise ValidationError("Cannot bulk create objects with different tenant")
                setattr(obj, TENANT_FIELD_NAME, tenant)

        return super().bulk_create(objs, *args, **kwargs)

    def bulk_update(self, objs, fields, *args, **kwargs):
        """Automatically checks the tenant on each object before bulk update."""
        tenant = get_current_tenant()

        for obj in objs:
            obj_tenant = getattr(obj, TENANT_FIELD_NAME, None)
            if obj_tenant and obj_tenant.id != tenant.id:
                raise ValidationError("Cannot bulk update objects from different tenant")

        return super().bulk_update(objs, fields, *args, **kwargs)


class TenantAwareAbstract(models.Model):
    """Abstract base model that associates each record with a specific tenant."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        current_tenant = get_current_tenant()
        
        if self.pk is None:
            # New object - set tenant
            setattr(self, TENANT_FIELD_NAME, current_tenant)
        else:
            # Existing object - prevent tenant switching
            existing_tenant = getattr(self, TENANT_FIELD_NAME, None)
            if existing_tenant and existing_tenant.id != current_tenant.id:
                raise ValidationError("Cannot change tenant after creation")

        super().save(*args, **kwargs)

    def get_tenant_instance(self) -> Optional[Tenant]:
        return getattr(self, TENANT_FIELD_NAME, None)


class TenantAwareModel(TenantAwareAbstract):
    """Abstract model associating records with specific tenant."""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="%(class)s_set",  # Creates tenant.product_set, tenant.order_set, etc.
        db_index=True
    )

    objects = TenantManager()

    class Meta:
        abstract = True


class UniqueTenantConstraint(UniqueConstraint):
    """Unique constraint scoped to tenant."""

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
