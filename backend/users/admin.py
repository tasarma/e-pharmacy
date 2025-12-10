from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser."""
    
    # Use all_objects to see all users in admin
    def get_queryset(self, request):
        return CustomUser.all_objects.get_queryset()
    
    list_display = ['email', 'tenant', 'role', 'is_active', 'is_staff']
    list_filter = ['tenant', 'role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Tenant', {'fields': ('tenant', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'tenant', 'role'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile."""
    
    # Use tenant_context_disabled for admin
    def get_queryset(self, request):
        from tenants.context import tenant_context_disabled
        with tenant_context_disabled():
            return super().get_queryset(request)
    
    list_display = ['user', 'tenant', 'phone_number']
    list_filter = ['tenant']
    search_fields = ['user__email']
