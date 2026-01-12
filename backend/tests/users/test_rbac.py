import pytest
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Product, Category
from tenants.context import set_tenant_context, tenant_context_disabled

@pytest.mark.django_db
class TestRBAC:
    """Test Role-Based Access Control and Tenant Isolation."""

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def category(self, manager):
        """Create a category for the manager's tenant."""
        with set_tenant_context(tenant=manager.tenant):
            return Category.objects.create(
                name="Test Category",
                slug="test-category",
                description="Test Description",
                is_active=True,
                display_order=1
            )

    def test_superadmin_can_access_all_tenants(self, client, superadmin, tenant, other_tenant):
        """Superadmin should be able to access data from any tenant."""
        client.force_authenticate(user=superadmin)

        # Access Tenant 1
        response = client.get(
            "/api/products/products/",
            HTTP_HOST=f"{tenant.subdomain}.example.com"
        )
        assert response.status_code == status.HTTP_200_OK

        # Access Tenant 2
        response = client.get(
            "/api/products/products/",
            HTTP_HOST=f"{other_tenant.subdomain}.example.com"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_manager_cannot_access_other_tenant(self, client, manager, other_tenant):
        """Manager should NOT be able to access another tenant's data."""
        client.force_authenticate(user=manager)

        # Try to access other tenant
        response = client.get(
            "/api/products/products/",
            HTTP_HOST=f"{other_tenant.subdomain}.example.com"
        )
        # Should return 404 (Tenant not found or User not found in tenant) 
        # or 403 (Forbidden) depending on implementation.
        # Given TenantAwareMiddleware, if the user is not in the tenant, 
        # they might be treated as anonymous or just fail authentication if the user check is strict.
        # But here, the user exists in DB but is linked to 'tenant'.
        # The middleware sets the tenant context based on Host.
        # The view checks permissions.
        
        # If the user is authenticated but accessing a different tenant, 
        # usually they shouldn't even be able to log in if the auth is tenant-scoped.
        # But if they are logged in, the system should block access.
        
        # Let's see what happens. Expecting 403 or 404.
        # Based on typical multi-tenant logic, a user from Tenant A shouldn't exist in Tenant B context.
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED]

    def test_regular_user_cannot_access_other_tenant(self, client, regular_user, other_tenant):
        """Regular user should NOT be able to access another tenant's data."""
        client.force_authenticate(user=regular_user)

        response = client.get(
            "/api/products/products/",
            HTTP_HOST=f"{other_tenant.subdomain}.example.com"
        )
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED]

    def test_manager_can_create_product(self, client, manager, category):
        """Manager (TenantAdmin) can create products."""
        client.force_authenticate(user=manager)

        response = client.post(
            "/api/products/products/",
            {
                "name": "Manager Product",
                "slug": "manager-product",
                "sku": "MGR-001",
                "price": "10.00",
                "category": category.id,
                "description": "Created by manager",
                "track_inventory": True,
                "stock_quantity": 100
            },
            format="json",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_regular_user_cannot_create_product(self, client, regular_user, category):
        """Regular user cannot create products (Read-Only)."""
        client.force_authenticate(user=regular_user)

        response = client.post(
            "/api/products/products/",
            {
                "name": "User Product",
                "slug": "user-product",
                "sku": "USR-001",
                "price": "10.00",
                "category": category.id,
                "description": "Created by user"
            },
            format="json",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
