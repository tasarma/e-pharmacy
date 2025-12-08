from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest
from tenants.context import get_current_tenant
from typing import Optional, Type, Any
import logging

logger = logging.getLogger(__name__)


class TenantAwareAuthBackend(ModelBackend):
    """
    Authenticate users within their tenant context.
    This ensures users can only log in to their assigned tenant.
    """

    def authenticate(
        self,
        request: HttpRequest,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[AbstractBaseUser]:
        UserModel: Type[AbstractBaseUser] = get_user_model()

        email: Optional[str] = kwargs.get(UserModel.USERNAME_FIELD) or username
        if email is None or password is None:
            return None

        try:
            tenant = get_current_tenant()
            if tenant is None or not tenant.active:
                logger.error("Authentication attempted without tenant context")
                return None

            user: AbstractBaseUser = UserModel.objects.get(email=email, tenant=tenant)

        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce timing attacks
            UserModel().set_password(password)
            logger.warning(
                f"Authentication failed: user '{email}' does not exist in tenant '{tenant.subdomain}'"
            )
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                if not user.tenant.active:
                    logger.warning(
                        "Login blocked for inactive tenant",
                        extra={"user_id": user.id, "tenant_id": tenant.id},
                    )
                    return None
                return user

        return None

    def get_user(self, user_id: Any) -> Optional[AbstractBaseUser]:
        """
        Override to ensure we only retrieve users from the current tenant.
        """
        UserModel: Type[AbstractBaseUser] = get_user_model()
        try:
            tenant = get_current_tenant()
            if tenant is None or not tenant.active:
                return None
            return UserModel.objects.get(pk=user_id, tenant=tenant)
        except UserModel.DoesNotExist:
            return None
