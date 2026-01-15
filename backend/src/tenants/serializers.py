from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from typing import Dict, Any

from .models import Tenant, TenantSettings
from .services import TenantOnboardingService
from .validators import validate_business_email, validate_tenant_name


class TenantSettingsSerializer(serializers.ModelSerializer):
    """Serializer for tenant settings management."""

    full_address = serializers.CharField(source="get_full_address", read_only=True)
    store_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = TenantSettings
        fields = [
            "tenant",
            "store_name",
            "store_description",
            "store_logo",
            "store_logo_url",
            "phone_number",
            "email",
            "website",
            "address_line1",
            "address_line2",
            "city",
            "state_province",
            "postal_code",
            "country",
            "full_address",
            "tax_id",
            "business_license",
            "operating_hours",
            "facebook_url",
            "twitter_url",
            "instagram_url",
            "linkedin_url",
            "allow_guest_checkout",
            "require_email_verification",
            "maintenance_mode",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_store_logo_url(self, obj) -> str | None:
        if obj.store_logo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.store_logo.url)
        return None

    def validate_operating_hours(self, value) -> Dict:
        """Validate operating hours structure."""
        if not value:
            return {}

        VALID_DAYS = {
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        }

        for day in value.keys():
            if day.lower() not in VALID_DAYS:
                raise serializers.ValidationError(f"Invalid day: {day}")

        return value


class TenantPublicInfoSerializer(serializers.ModelSerializer):
    """Public-facing tenant information (no sensitive data)."""

    settings = TenantSettingsSerializer(read_only=True)

    class Meta:
        model = Tenant
        fields = ["name", "subdomain", "settings"]


class TenantOnboardingSerializer(serializers.Serializer):
    """Public endpoint for tenant signup."""

    # Tenant info
    tenant_name = serializers.CharField(max_length=100)
    subdomain = serializers.CharField(max_length=60)

    # Manager user info
    manager_email = serializers.EmailField()
    manager_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    manager_first_name = serializers.CharField(max_length=150, required=True)
    manager_last_name = serializers.CharField(max_length=150, required=True)

    store_name = serializers.CharField(
        max_length=200, required=False, help_text="If not provided, uses tenant_name"
    )
    store_phone = serializers.CharField(max_length=17, required=False, allow_blank=True)
    store_email = serializers.EmailField(
        required=False, help_text="Public store email (defaults to manager_email)"
    )

    def validate_subdomain(self, value: str) -> str:
        """Ensure subdomain is available."""
        value = value.lower().strip()

        if Tenant.objects.filter(subdomain=value).exists():
            raise serializers.ValidationError("Subdomain already taken")

        return value

    def validate_manager_password(self, value: str) -> str:
        """Use Django's password validators."""
        validate_password(value)
        return value

    def validate_manager_email(self, value: str) -> str:
        """Check if email is globally unique (across all tenants)."""
        validate_business_email(value)
        from users.models import CustomUser

        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already registered. Please use a different email."
            )

        return value

    def validate_tenant_name(self, value: str) -> str:
        validate_tenant_name(value)
        return value

    def create(self, validated_data: Dict[str, Any]) -> Tenant:
        """Create tenant with manager user."""

        store_settings = {
            "store_name": validated_data.pop(
                "store_name", validated_data["tenant_name"]
            ),
            "phone_number": validated_data.pop("store_phone", ""),
            "email": validated_data.pop("store_email", validated_data["manager_email"]),
        }

        result = TenantOnboardingService.create_tenant_with_manager(
            name=validated_data["tenant_name"],
            subdomain=validated_data["subdomain"],
            manager_email=validated_data["manager_email"],
            manager_password=validated_data["manager_password"],
            manager_first_name=validated_data.get("manager_first_name", ""),
            manager_last_name=validated_data.get("manager_last_name", ""),
            metadata=store_settings,
        )

        return result
