import pytest
from rest_framework.test import APIClient
from products.models import ProductTag
from tenants.context import set_tenant_context


@pytest.mark.django_db
class TestProductTagAPI:
    """Test Product Tag API endpoints."""

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_list_tags(self, client, manager, product_tag):
        """Test listing tags."""
        client.force_authenticate(user=manager)

        response = client.get(
            "/api/products/tags/", HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
        )

        assert response.status_code == 200
        assert len(response.data) > 0

    def test_create_tag(self, client, manager):
        """Test creating a new tag."""
        client.force_authenticate(user=manager)

        response = client.post(
            "/api/products/tags/",
            {"name": "New Tag", "slug": "new-tag"},
            format="json",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 201
        assert response.data["name"] == "New Tag"

    def test_delete_tag(self, client, manager, product_tag):
        """Test deleting a tag."""
        client.force_authenticate(user=manager)

        response = client.delete(
            f"/api/products/tags/{product_tag.id}/",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 204
        with set_tenant_context(tenant=manager.tenant):
            assert not ProductTag.objects.filter(id=product_tag.id).exists()
