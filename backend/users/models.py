from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from typing import Any
from django.core.checks import Error

from tenants.models import Tenant, UniqueTenantConstraint
from users.managers import CustomUserManager

# from ..regex_validators import phone_validator
from config.regex_validators import phone_validator


ERROR_AUTH_EO33 = "auth.E003"


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

    objects = CustomUserManager()

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


class UserProfile(models.Model):
    """Business data and application-specific user information."""

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="profiles"
    )

    # Contact Information
    phone_number = models.CharField(
        max_length=20, blank=True, validators=[phone_validator]
    )

    # Personal Details
    # first_name = models.CharField(max_length=150, blank=True)
    # last_name = models.CharField(max_length=150, blank=True)
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
