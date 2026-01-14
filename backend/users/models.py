from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid
from typing import Any
from django.core.checks import Error

from tenants.models import Tenant, TenantAwareModel, UniqueTenantConstraint
from users.managers import CustomUserManager, TenantAwareUserManager

from utils.regex_validators import phone_validator


ERROR_AUTH_EO33 = "auth.E003"

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message=_(
        "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    ),
)


class CustomUser(AbstractUser):
    """
    Minimal user model - authentication only.
    """

    username = None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        _("email address"), blank=False, null=False, db_index=True
    )
    tenant = models.ForeignKey(
        Tenant,
        related_name="users",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("user", "User"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = TenantAwareUserManager()  # Filters by tenant
    all_objects = CustomUserManager()  # For admin/superuser use

    class Meta:
        constraints = [
            UniqueTenantConstraint(fields=["email"], name="unique_tenant_email")
        ]

        indexes = [
            models.Index(fields=["tenant", "email"], name="idx_tenant_email"),
        ]

    def __str__(self) -> str:
        return self.email

    @classmethod
    def check(cls, **kwargs: Any) -> list[Error]:
        """
        Override Django's system checks to allow USERNAME_FIELD in composite constraint.
        This is necessary for multi-tenant setups where email must be unique per tenant.
        """
        errors: list[Error] = super().check(**kwargs)
        # Remove auth.E003 since we're using a composite constraint
        errors = [e for e in errors if e.id != ERROR_AUTH_EO33]
        return errors


class UserProfile(TenantAwareModel):
    """Business data and application-specific user information."""

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )

    # Contact Information
    phone_number = models.CharField(
        max_length=20, blank=True, validators=[phone_validator]
    )

    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    gln_number = models.CharField(max_length=13, blank=True, null=True)

    # Preferences
    email_notifications = models.BooleanField(default=False)

    # Metadata - consider anonymizing/deleting old IPs per GDPR
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueTenantConstraint(fields=["user"], name="unique_tenant_user_profile"),
            UniqueTenantConstraint(fields=["gln_number"], name="unique_tenant_gln"),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} - Profile"

    @property
    def display_name(self) -> str:
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.email

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}".strip()
