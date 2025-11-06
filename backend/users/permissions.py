from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission:
    - Admin/Manager: full access to all profiles in tenant
    - Regular users: read/write access to their own profile only
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can access this specific profile.
        """
        user = request.user
        
        # Admins and managers have full access
        if user.role in ['admin', 'manager']:
            return True
        
        # Users can only access their own profile
        return obj.user == user
