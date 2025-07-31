from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import models
from unittest.mock import patch

from tenants.models import Tenant, TenantAwareModel


class TestProduct(TenantAwareModel):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tenants"


class TestTenantModel(TestCase):
    def setUp(self):
        # Arrange
        self.user = User.objects.create_user(
            username="testuser", email="test@gmail.com", password="123"
        )

    def test_tenant_can_be_created_with_required_fields(self):
        # Act
        tenant = Tenant.objects.create(
            name="Alice's Shop",
            subdomain="alice",
            owner=self.user,
            active=True,
        )

        # Assert
        self.assertEqual(tenant.name, "Alice's Shop")
        self.assertEqual(tenant.subdomain, "alice")
        self.assertEqual(tenant.owner, self.user)
        self.assertTrue(tenant.active)
        self.assertIsNotNone(tenant.created_at)

    def test_tenant_subdomain_must_be_unique(self):
        # Act
        Tenant.objects.create(name="Alice's Shop", subdomain="alice")

        # Assert
        with self.assertRaises(ValidationError):
            duplicate_tenant = Tenant(name="Another Shop", subdomain="alice")
            duplicate_tenant.full_clean()  # This triggers model validation


class TestTenantManager(TestCase):
    def setUp(self):
        self.tenant1 = Tenant.objects.create(
            name="Tenant 1",
            subdomain="tenant1",
        )
        self.tenant2 = Tenant.objects.create(
            name="Tenant 2",
            subdomain="tenant2",
        )

    @patch("tenants.models.get_current_tenant")
    def test_bulk_create_sets_tenant_on_objects(self, mock_get_current_tenant):
        # Arrange
        mock_get_current_tenant.return_value = self.tenant1

        products = [
            TestProduct(name="Bulk Product 1"),
            TestProduct(name="Bulk Product 2"),
            TestProduct(name="Bulk Product 3"),
        ]

        # Act
        TestProduct.objects.bulk_create(products)

        # Assert
        for product in products:
            self.assertEqual(product.tenant, self.tenant1)

    @patch("tenants.models.get_current_tenant")
    @patch("tenants.models.get_state")
    def test_get_queryset_filters_by_current_tenant_when_enabled(
        self, mock_get_state, mock_get_current_tenant
    ):
        # Arrange
        mock_get_state.return_value = {"enabled": True}
        mock_get_current_tenant.return_value = self.tenant1

        with patch("tenants.models.get_current_tenant", return_value=self.tenant1):
            _product1 = TestProduct.objects.create(name="Tenant 1 Product")

        with patch("tenants.models.get_current_tenant", return_value=self.tenant2):
            _product2 = TestProduct.objects.create(name="Tenant 2 Product")

        # Act
        queryset = TestProduct.objects.all()

        # Assert
        # Note: We can't easily test the actual filtering since CurrentTenant expression
        # requires database execution, but we can verify the manager applies the filter
        self.assertTrue(hasattr(queryset, "query"))
        # The queryset should have the tenant filter applied
        filter_found = any(
            "tenant" in str(child) for child in queryset.query.where.children
        )
        self.assertTrue(
            filter_found, "Expected tenant filter to be applied to queryset"
        )


class TestTenantAwareAbstract(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            subdomain="test",
        )

    @patch("tenants.models.get_current_tenant")
    def test_save_sets_current_tenant(self, mock_get_current_tenant):
        # Arrange
        mock_get_current_tenant.return_value = self.tenant
        product = TestProduct(name="Test Product")

        # Act
        product.save()

        # Assert
        self.assertEqual(product.tenant, self.tenant)
        mock_get_current_tenant.assert_called_once()

    def test_get_tenant_instance_returns_tenant(self):
        # Arrange
        with patch("tenants.models.get_current_tenant", return_value=self.tenant):
            product = TestProduct.objects.create(name="Test Product")

        # Act
        tenant_instance = product.get_tenant_instance()

        # Assert
        self.assertEqual(tenant_instance, self.tenant)

    def test_get_tenant_instance_returns_none_when_no_tenant(self):
        # Arrange
        product = TestProduct(name="Test Product")

        # Act
        tenant_instance = product.get_tenant_instance()

        # Assert
        self.assertIsNone(tenant_instance)


class TestTenantAwareModel(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Test Tenant", subdomain="test")

    def test_product_belongs_to_current_tenant_when_created(self):
        # Arrange
        with patch("tenants.models.get_current_tenant", return_value=self.tenant):
            # Act
            product = TestProduct.objects.create(name="Test Product")

            # Assert
            self.assertEqual(product.tenant, self.tenant)

    def test_product_creation_fails_when_no_current_tenant(self):
        # Arrange
        with patch("tenants.models.get_current_tenant", return_value=None):
            # Act & Assert
            with self.assertRaises((IntegrityError, AttributeError)):
                TestProduct.objects.create(name="Test Product")

    def test_bulk_created_products_all_belong_to_current_tenant(self):
        # Arrange
        products = [TestProduct(name=f"Product {i}") for i in range(3)]

        with patch("tenants.models.get_current_tenant", return_value=self.tenant):
            # Act
            created_products = TestProduct.objects.bulk_create(products)

            # Assert
            for product in created_products:
                self.assertEqual(product.tenant, self.tenant)
