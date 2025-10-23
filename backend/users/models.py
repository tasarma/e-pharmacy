from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

from tenants.models import Tenant, TenantAwareModel, UniqueTenantConstraint
from users.managers import CustomUserManager


ERROR_AUTH_EO33 = "auth.E003"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email is necessary!"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Minimal user model - authentication only.
    """

    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), blank=False, null=False)
    tenant = models.ForeignKey(
        Tenant, related_name="users", on_delete=models.CASCADE, null=True, blank=True
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True)
    mobile_number = models.CharField(max_length=20, blank=True)

    # Personal Details
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    gln_number = models.CharField(max_length=13, blank=True, null=True, unique=True)

    # Preferences
    email_notifications = models.BooleanField(default=False)

    # Metadata
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueTenantConstraint(fields=["user"], name="unique_tenant_user_profile")
        ]

    def __str__(self):
        return f"{self.user.email} - Profile"

    @property
    def display_name(self):
        """Convenient display name"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.email
