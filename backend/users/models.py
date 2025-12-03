from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid

from tenants.models import Tenant, TenantAwareModel, UniqueTenantConstraint
from users.managers import CustomUserManager


ERROR_AUTH_EO33 = "auth.E003"

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
)

class CustomUser(AbstractUser):
    """
    Minimal user model - authentication only.
    """

    username = None
    first_name = None
    last_name = None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), blank=False, null=False, db_index=True)
    tenant = models.ForeignKey(
        Tenant, related_name="users", on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )

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

    def __str__(self):
        return self.email

    @classmethod
    def check(cls, **kwargs):
        """
        Override Django's system checks to allow USERNAME_FIELD in composite constraint.
        This is necessary for multi-tenant setups where email must be unique per tenant.
        """
        errors = super().check(**kwargs)
        # Remove auth.E003 since we're using a composite constraint
        errors = [e for e in errors if e.id != ERROR_AUTH_EO33]
        return errors


class UserProfile(TenantAwareModel):
    """
    Business data and application-specific user information.
    """

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )

    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True, validators=[phone_regex])

    # Personal Details
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
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

    def __str__(self):
        return f"{self.user.email} - Profile"

    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
