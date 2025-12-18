import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestTenantSettingsAPI:
    """Test Tenant Settings API endpoints."""

    @pytest.fixture
    def client(self) -> APIClient:
        return APIClient()

    def test_get_settings_as_manager(self, client, manager, tenant_settings):
        client.force_authenticate(user=manager)

        host = f"{manager.tenant.subdomain}.example.com"

        # with set_tenant_context(tenant=manager.tenant):
        response = client.get(
            "/api/tenants/settings/",
            HTTP_HOST=host,
        )

        assert response.status_code == 200
        assert "store_name" in response.data

    def test_regular_user_cannot_update(self, client, regular_user, tenant_settings):
        """Regular users should be forbidden from updating tenant settings."""
        client.force_authenticate(user=regular_user)

        host = f"{regular_user.tenant.subdomain}.example.com"

        # with set_tenant_context(tenant=regular_user.tenant):
        response = client.patch(
            "/api/tenants/settings/",
            {"store_name": "Unauthorized"},
            format="json",
            HTTP_HOST=host,
        )

        assert response.status_code == 403
