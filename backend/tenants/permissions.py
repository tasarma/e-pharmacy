from rest_framework.permissions import BasePermission


class IsTenantManager(BasePermission):
    """
    Permission check: User must be admin of current tenant.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['admin', 'manager']
        )
