import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from products.models import Product, Category
from tenants.context import set_tenant_context


@pytest.mark.django_db
class TestCategoryAPI:
    """Test Category API endpoints."""

    def test_list_categories_authenticated(self, client, manager, category):
        """Test authenticated user can list categories."""
        client.force_authenticate(user=manager)

        response = client.get(
            "/api/products/categories/",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        assert len(response.data) > 0

    def test_list_categories_unauthenticated(self, client, manager):
        """Test unauthenticated user cannot list categories."""
        # Even unauthenticated requests need a tenant context via host
        response = client.get(
            "/api/products/categories/",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )
        assert response.status_code == 401

    def test_create_category_as_admin(self, client, manager):
        """Test admin can create category."""
        client.force_authenticate(user=manager)

        response = client.post(
            "/api/products/categories/",
            {
                "name": "New Category",
                "slug": "new-category",
                "description": "Test",
                "is_active": True,
            },
            format="json",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 201
        assert response.data["name"] == "New Category"

    def test_create_category_as_regular_user(self, client, regular_user):
        """Test regular user cannot create category."""
        client.force_authenticate(user=regular_user)

        response = client.post(
            "/api/products/categories/",
            {"name": "New Category", "slug": "new-category"},
            format="json",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com",
        )

        assert response.status_code == 403

    def test_get_category_children(
        self, client, manager, parent_category, child_category
    ):
        """Test getting category children."""
        client.force_authenticate(user=manager)

        response = client.get(
            f"/api/products/categories/{parent_category.id}/children/",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        assert len(response.data) > 0

    def test_update_category(self, client, manager, category):
        """Test updating a category."""
        client.force_authenticate(user=manager)

        response = client.patch(
            f"/api/products/categories/{category.id}/",
            {"name": "Updated Category"},
            format="json",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        assert response.data["name"] == "Updated Category"

    def test_delete_category(self, client, manager, category):
        """Test deleting a category."""
        client.force_authenticate(user=manager)

        response = client.delete(
            f"/api/products/categories/{category.id}/",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 204
        with set_tenant_context(tenant=manager.tenant):
            assert not Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db
class TestProductAPI:
    """Test Product API endpoints."""

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_list_products_authenticated(self, client, regular_user, product):
        """Test authenticated user can list products."""
        client.force_authenticate(user=regular_user)

        response = client.get(
            "/api/products/products/",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        assert len(response.data) > 0

    def test_list_products_filters_inactive_for_regular_users(
        self, client, regular_user, product, tenant, category
    ):
        """Test regular users only see active products."""
        # Create inactive product
        # We need to manually set context here because we are using the ORM directly
        with set_tenant_context(tenant=tenant):
            inactive = Product.objects.create(
                name="Inactive Product",
                slug="inactive",
                sku="INACTIVE",
                category=category,
                price=Decimal("10.00"),
                is_active=False,
            )

        client.force_authenticate(user=regular_user)

        response = client.get(
            "/api/products/products/",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com",
        )

        product_ids = [p["id"] for p in response.data]
        assert str(product.id) in product_ids
        assert str(inactive.id) not in product_ids

    def test_get_product_detail(self, client, regular_user, product):
        """Test getting product detail."""
        client.force_authenticate(user=regular_user)

        response = client.get(
            f"/api/products/products/{product.id}/",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        assert response.data["name"] == product.name
        assert response.data["sku"] == product.sku

    def test_create_product_as_admin(self, client, manager, category):
        """Test admin can create product."""
        client.force_authenticate(user=manager)

        response = client.post(
            "/api/products/products/",
            {
                "name": "New Product",
                "slug": "new-product",
                "sku": "NEW-001",
                "description": "Test product",
                "category": str(category.id),
                "price": "49.99",
                "stock_quantity": 50,
                "track_inventory": True,
            },
            format="json",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 201
        assert response.data["name"] == "New Product"

    def test_create_product_as_regular_user_fails(self, client, regular_user, category):
        """Test regular user cannot create product."""
        client.force_authenticate(user=regular_user)

        response = client.post(
            "/api/products/products/",
            {
                "name": "New Product",
                "slug": "new-product",
                "sku": "NEW-001",
                "category": str(category.id),
                "price": "49.99",
            },
            format="json",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com",
        )

        assert response.status_code == 403

    def test_update_product_as_admin(self, client, manager, product):
        """Test admin can update product."""
        client.force_authenticate(user=manager)

        response = client.patch(
            f"/api/products/products/{product.id}/",
            {"name": "Updated Name"},
            format="json",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        assert response.data["name"] == "Updated Name"

    def test_adjust_stock(self, client, manager, product):
        """Test adjusting product stock."""
        client.force_authenticate(user=manager)
        initial_stock = product.stock_quantity

        response = client.post(
            f"/api/products/products/{product.id}/adjust_stock/",
            {"quantity": 10, "reason": "restock", "notes": "Weekly restock"},
            format="json",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        assert response.data["new_stock"] == initial_stock + 10

    def test_adjust_stock_insufficient(self, client, manager, product):
        """Test cannot adjust stock below zero."""
        client.force_authenticate(user=manager)

        response = client.post(
            f"/api/products/products/{product.id}/adjust_stock/",
            {"quantity": -1000, "reason": "sale"},
            format="json",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 400

    def test_get_stock_history(self, client, manager, product):
        """Test getting stock movement history."""
        # Create some movements
        # Must set context for ORM operations
        with set_tenant_context(tenant=manager.tenant):
            product.adjust_stock(10, reason="restock")
            product.adjust_stock(-5, reason="sale")

        client.force_authenticate(user=manager)

        response = client.get(
            f"/api/products/products/{product.id}/stock_history/",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        assert len(response.data) == 2

    def test_get_low_stock_products(self, client, manager, low_stock_product, product):
        """Test getting low stock products."""
        client.force_authenticate(user=manager)

        response = client.get(
            "/api/products/products/low_stock/",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        product_ids = [p["id"] for p in response.data]
        assert str(low_stock_product.id) in product_ids
        assert str(product.id) not in product_ids  # Not low stock

    def test_get_out_of_stock_products(
        self, client, manager, out_of_stock_product, product
    ):
        """Test getting out of stock products."""
        client.force_authenticate(user=manager)

        response = client.get(
            "/api/products/products/out_of_stock/",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        product_ids = [p["id"] for p in response.data]
        assert str(out_of_stock_product.id) in product_ids
        assert str(product.id) not in product_ids

    def test_get_featured_products(self, client, regular_user, tenant, category):
        """Test getting featured products."""
        with set_tenant_context(tenant=tenant):
            featured = Product.objects.create(
                name="Featured Product",
                slug="featured",
                sku="FEAT-001",
                category=category,
                price=Decimal("29.99"),
                is_featured=True,
                is_active=True,
            )

        client.force_authenticate(user=regular_user)

        response = client.get(
            "/api/products/products/featured/",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        product_ids = [p["id"] for p in response.data]
        assert str(featured.id) in product_ids

    def test_filter_products_by_category(self, client, regular_user, product, category):
        """Test filtering products by category."""
        client.force_authenticate(user=regular_user)

        response = client.get(
            f"/api/products/products/?category={category.id}",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        assert len(response.data) > 0

    def test_filter_products_by_price_range(self, client, regular_user, product):
        """Test filtering products by price."""
        client.force_authenticate(user=regular_user)

        response = client.get(
            "/api/products/products/?min_price=50&max_price=150",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        # Product price is 99.99, should be in range
        product_ids = [p["id"] for p in response.data]
        assert str(product.id) in product_ids

    def test_search_products(self, client, regular_user, product):
        """Test searching products."""
        client.force_authenticate(user=regular_user)

        response = client.get(
            f"/api/products/products/?search={product.name}",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200
        assert len(response.data) > 0

    def test_delete_product(self, client, manager, product):
        """Test deleting a product."""
        client.force_authenticate(user=manager)

        response = client.delete(
            f"/api/products/products/{product.id}/",
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 204
        with set_tenant_context(tenant=manager.tenant):
            assert not Product.objects.filter(id=product.id).exists()
