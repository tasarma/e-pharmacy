from rest_framework.permissions import BasePermission, SAFE_METHODS
from tenants.context import get_current_tenant


class IsStaffOrReadOnly(BasePermission):
    """
    Allow read-only for all authenticated users.
    Write permissions only for staff (admin/manager).
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["admin", "manager"]
        )


class IsTenantUser(BasePermission):
    """
    Ensure the user belongs to the current tenant context.
    Superadmins are exempt.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superadmins can access everything
        if request.user.is_superuser:
            return True

        current_tenant = get_current_tenant()

        if not current_tenant:
            return False

        # Check if user's tenant matches current tenant
        return request.user.tenant == current_tenant
