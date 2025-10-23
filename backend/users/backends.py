from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from tenants.context import get_current_tenant


class TenantAwareAuthBackend(ModelBackend):
    """
    Authenticate users within their tenant context.
    This ensures users can only log in to their assigned tenant.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        if username is None:
            email = kwargs.get(UserModel.USERNAME_FIELD)

        if email is None:
            return None

        try:
            tenant = get_current_tenant()
            if tenant is None:
                return None

            user = UserModel.objects.get(email=email, tenant=tenant)

        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce timing attacks
            UserModel().set_password(password)
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        return None

    def get_user(self, user_id):
        """
        Override to ensure we only retrieve users from the current tenant.
        """
        UserModel = get_user_model()
        try:
            tenant = get_current_tenant()
            if tenant is None:
                return None
            return UserModel.objects.get(pk=user_id, tenant=tenant)
        except UserModel.DoesNotExist:
            return None
