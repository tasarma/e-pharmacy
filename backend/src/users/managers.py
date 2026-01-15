from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from tenants.context import get_state, get_current_tenant
from tenants.models import CurrentTenant, TENANT_FIELD_NAME


class CustomUserManager(BaseUserManager):
    """
    Custom user manager that uses email as the unique identifier
    and enforces tenant context for regular users.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError(_("Email is necessary!"))
        try:
            validate_email(email)
        except ValidationError as e:
            raise ValueError(_("Invalid email format")) from e

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not password:
            raise ValueError(_("Superuser must have a password"))

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class TenantAwareUserManager(CustomUserManager):
    """
    Manager that automatically filters users by current tenant.
    Used as default manager for CustomUser.
    """

    def get_queryset(self):
        """Filter by current tenant when enabled."""
        state = get_state()
        base_queryset = super().get_queryset()

        if not state.get("enabled", True):
            return base_queryset

        # Cache field lookup
        if not hasattr(self, "_tenant_field_cache"):
            self._tenant_field_cache = self.model._meta.get_field(
                TENANT_FIELD_NAME
            ).target_field

        filter_kwargs = {
            TENANT_FIELD_NAME: CurrentTenant(output_field=self._tenant_field_cache)
        }
        return base_queryset.filter(**filter_kwargs)

    def create_user(self, email, password=None, **extra_fields):
        """Override to set tenant on user creation."""
        # If tenant not explicitly set and context enabled
        if "tenant" not in extra_fields:
            try:
                state = get_state()
                if state.get("enabled", True):
                    extra_fields["tenant"] = get_current_tenant()
            except Exception:
                pass  # Allow creation without tenant in disabled context

        return super().create_user(email, password, **extra_fields)
