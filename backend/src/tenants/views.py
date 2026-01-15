from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.throttling import AnonRateThrottle
from drf_spectacular.utils import extend_schema
import structlog
from typing import Any, Dict


from .models import TenantSettings
from .serializers import TenantSettingsSerializer, TenantOnboardingSerializer
from .context import get_current_tenant
from .permissions import IsTenantManager

logger = structlog.get_logger(__name__)


class TenantSettingsView(APIView):
    """
    Singleton tenant settings manager.
    Each tenant has exactly one settings object.
    Only accessible by superadmin and tenant manager.
    """

    serializer_class = TenantSettingsSerializer
    permission_classes = [IsAuthenticated, IsTenantManager]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self) -> TenantSettings:
        tenant = get_current_tenant()
        settings, created = TenantSettings.objects.get_or_create(
            tenant=tenant,
            defaults={
                "store_name": tenant.name,
                "email": f"contact@{tenant.subdomain}.example.com",
            },
        )

        if created:
            logger.info("tenant_settings_created", tenant_id=str(tenant.id))

        return settings

    def get_serializer(self, *args: Any, **kwargs: Any) -> TenantSettingsSerializer:
        kwargs.setdefault("context", {"request": self.request})
        return self.serializer_class(*args, **kwargs)

    def _save(
        self, instance: TenantSettings, data: Dict[str, Any], partial: bool
    ) -> Dict[str, Any]:
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(
            "tenant_settings_updated",
            tenant_id=str(instance.tenant.id),
            updated_fields=list(data.keys()),
        )

        return serializer.data

    @extend_schema(
        responses={200: TenantSettingsSerializer},
        description="Get current tenant settings",
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance: TenantSettings = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        request=TenantSettingsSerializer,
        responses={200: TenantSettingsSerializer},
        description="Fully update tenant settings",
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        partial: bool = kwargs.pop("partial", False)
        instance: TenantSettings = self.get_object()
        data = self._save(
            instance,
            data=request.data,
            partial=partial,  # , context={"request": request}
        )

        return Response(data)

    @extend_schema(
        request=TenantSettingsSerializer,
        responses={200: TenantSettingsSerializer},
        description="Partial update of tenant settings",
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        kwargs["partial"] = True
        instance: TenantSettings = self.get_object()
        data = self._save(instance, request.data, partial=True)
        return Response(data)

    @extend_schema(description="Delete tenant store logo.")
    def delete_logo(self, request: Request) -> Response:
        settings: TenantSettings = self.get_object()

        if settings.store_logo:
            settings.store_logo.delete(save=True)
            logger.info("tenant_logo_deleted", tenant_id=str(settings.tenant.id))
            return Response({"message": "Logo deleted successfully"})

        return Response(
            {"message": "No logo to delete"}, status=status.HTTP_404_NOT_FOUND
        )


class TenantOnboardingThrottle(AnonRateThrottle):
    """Rate limit tenant creation to prevent abuse."""

    rate = "10/hour"  # Max 3 tenant creations per IP per hour


class TenantOnboardingView(APIView):
    """
    Public endpoint for tenant registration.
    No authentication required.
    """

    permission_classes = [AllowAny]
    throttle_classes = [TenantOnboardingThrottle]

    @extend_schema(
        request=TenantOnboardingSerializer,
        responses={201: TenantOnboardingSerializer},
        description="Create new tenant with manager user",
    )
    def post(self, request: Request) -> Response:
        serializer = TenantOnboardingSerializer(data=request.data)

        if not serializer.is_valid():
            logger.warning(
                "tenant_onboarding_validation_error",
                errors=serializer.errors,
                ip=request.META.get("REMOTE_ADDR"),
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = serializer.save()

            logger.info(
                "tenant_onboarded_successfully",
                tenant_id=str(result["tenant"].id),
                subdomain=result["tenant"].subdomain,
                manager_email=result["manager_user"].email,
                ip=request.META.get("REMOTE_ADDR"),
            )

            return Response(
                {
                    "message": result["message"],
                    "tenant": {
                        "id": str(result["tenant"].id),
                        "name": result["tenant"].name,
                        "subdomain": result["tenant"].subdomain,
                    },
                    "manager": {
                        "id": str(result["manager_user"].id),
                        "email": result["manager_user"].email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(
                "tenant_onboarding_exception",
                error=str(e),
                ip=request.META.get("REMOTE_ADDR"),
                exc_info=True,
            )
            return Response(
                {"error": "Failed to create tenant. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
