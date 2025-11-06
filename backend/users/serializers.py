from djoser.serializers import UserCreateSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from tenants.context import get_current_tenant
from rest_framework import serializers

from tenants.exceptions import TenantError
from .models import CustomUser, UserProfile


class TenantAwareTokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        current_tenant = get_current_tenant()

        if self.user.tenant_id != current_tenant.id:
            raise serializers.ValidationError(
                f"user doesn't belong to tenant '{current_tenant.name}'."
            )

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        if user.tenant:
            token["tenant_subdomain"] = user.tenant.subdomain
        return token


class TenantAwareUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ("id", "email", "password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        validated_data.pop("tenant", None)
        validated_data["role"] = "user"

        try:
            tenant = get_current_tenant()
        except TenantError as exc:
            raise serializers.ValidationError({"tenant": str(exc)})

        if not tenant or not getattr(tenant, "active", True):
            raise serializers.ValidationError(
                {"tenant": "No active tenant in context."}
            )

        validated_data["tenant"] = tenant
        user = super().create(validated_data)

        return user


# =============
# Profile
# =============


class UserProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "user_email",
            "phone_number",
            "mobile_number",
            "first_name",
            "last_name",
            "date_of_birth",
            "address",
            "gln_number",
            "email_notifications",
            "last_login_ip",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at", "last_login_ip"]

    def validate_gln_number(self, value):
        """Validate GLN number format (13 digits)."""
        if value and not value.isdigit():
            raise serializers.ValidationError("GLN must contain only digits.")
        if value and len(value) != 13:
            raise serializers.ValidationError("GLN must be exactly 13 digits.")
        return value

    def validate(self, attrs):
        """Additional validation for profile data."""
        # Ensure first_name and last_name are provided
        if not attrs.get("first_name"):
            raise serializers.ValidationError({"first_name": "First name is required."})
        if not attrs.get("last_name"):
            raise serializers.ValidationError({"last_name": "Last name is required."})
        return attrs
