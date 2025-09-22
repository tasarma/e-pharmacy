from djoser.serializers import UserCreateSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from tenants.context import get_current_tenant
from rest_framework import serializers

from tenants.exceptions import TenantError
from .models import CustomUser


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
