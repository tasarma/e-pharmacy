from typing import Any, Type
from djoser.serializers import UserCreateSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from tenants.context import get_current_tenant
from rest_framework import serializers

from tenants.exceptions import TenantError
from .models import CustomUser


class TenantAwareTokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(attrs)

        try:
            current_tenant = get_current_tenant()
        except TenantError:
            raise serializers.ValidationError("Authentication failed.")

        if self.user.tenant_id != current_tenant.id:
            raise serializers.ValidationError("Authentication failed.")

        return data


    @classmethod
    def get_token(
        cls: Type["TenantAwareTokenObtainSerializer"], user: CustomUser
    ) -> Token:
        token: Token = super().get_token(user)
        if user.tenant_id:
            token["tenant_id"] = str(user.tenant_id)
            # Only add subdomain if needed by frontend
            # if user.tenant:
            #     token["tenant_subdomain"] = user.tenant.subdomain
        return token


class TenantAwareUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ("id", "email", "password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data: dict[str, Any]) -> CustomUser:
        validated_data.pop("tenant", None)
        validated_data["role"] = "user"

        try:
            tenant = get_current_tenant()
        except TenantError:
            raise serializers.ValidationError(
                {"detail": "Tenant context required for registration."}
            )

        if not tenant.active:
            raise serializers.ValidationError({"detail": "Registration not available."})

        validated_data["tenant"] = tenant
        user = super().create(validated_data)

        return user
