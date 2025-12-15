import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory
from tenants.permissions import IsTenantManager


@pytest.mark.django_db(transaction=True)
class TestTenantPermissions:
    """Test tenant permission classes using parameterization."""

    @pytest.mark.parametrize(
        "user,expected",
        [("manager", True), ("regular_user", False), ("anonymous", False)],
    )
    def test_tenant_permission(self, user, expected, manager, regular_user):
        factory = APIRequestFactory()
        request = factory.get("/")

        request.user = {
            "manager": manager,
            "regular_user": regular_user,
            "anonymous": AnonymousUser(),
        }[user]

        permission = IsTenantManager()
        assert permission.has_permission(request, None) is expected
