from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from .models import UserProfile
from .serializers import UserProfileSerializer
from tenants.context import get_current_tenant


class UserProfileViewSet(viewsets.GenericViewSet):
    """
    ViewSet to manage the authenticated user's profile.
    Only allows access to the current user's profile within the current tenant.


    Users can only view/edit their own profile unless they're admin/manager.

    Note: No create endpoint - profiles are auto-created via signals on user registration.
    No PUT endpoint - use PATCH for updates only.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['email_notifications', 'first_name', 'last_name']
    # search_fields = ['first_name', 'last_name', 'user__email', 'phone_number', 'gln_number']
    # ordering_fields = ['created_at', 'updated_at', 'last_name', 'first_name']
    # ordering = ['-created_at']
    http_method_names = ["get", "patch", "put"]

    def get_object(self):
        """
        Return the profile of the currently authenticated user.
        Ensures tenant isolation by relying on TenantAwareModel's manager.
        """
        tenant = get_current_tenant()
        if not tenant:
            # Should not happen due to middleware, but safe guard
            raise PermissionError("No active tenant in context.")

        profile = get_object_or_404(UserProfile, user=self.request.user)
        return profile

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        summary="Get current user's profile",
        description="Convenient shortcut endpoint: /profiles/me/ instead of /profiles/123/me/",
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get the current user's profile."""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )
