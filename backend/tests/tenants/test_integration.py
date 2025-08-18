from django.test import TestCase
from unittest.mock import patch

from tenants.models import Tenant
from tests.models import TestOrder


class TestTenantSystemIntegration(TestCase):
    def setUp(self):
        self.tenant1 = Tenant.objects.create(
            name="Tenant 1",
            subdomain="tenant1",
        )
        self.tenant2 = Tenant.objects.create(
            name="Tenant 2",
            subdomain="tenant2",
        )

    def test_complete_tenant_workflow(self):
        """End-to-end test of tenant creation and usage"""

        # Act
        tenant = Tenant.objects.create(
            name="Complete Test Tenant", subdomain="complete"
        )

        with patch("tenants.models.get_current_tenant", return_value=tenant):
            products = TestOrder.objects.bulk_create(
                [
                    TestOrder(name="Integration Product 1"),
                    TestOrder(name="Integration Product 2"),
                ]
            )

        # Assert
        self.assertEqual(len(products), 2)
        for product in products:
            self.assertEqual(product.tenant, tenant)
            self.assertEqual(product.get_tenant_instance(), tenant)

    def test_tenant_isolation_in_queries(self):
        # Create products for tenant1
        with patch("tenants.models.get_current_tenant", return_value=self.tenant1):
            product1 = TestOrder.objects.create(name="Product 1")
            product2 = TestOrder.objects.create(name="Product 2")

        # Create products for tenant2
        with patch("tenants.models.get_current_tenant", return_value=self.tenant2):
            product3 = TestOrder.objects.create(name="Product 3")

        # Verify products were created with correct tenants
        product1.refresh_from_db()
        product2.refresh_from_db()
        product3.refresh_from_db()

        self.assertEqual(product1.tenant, self.tenant1)
        self.assertEqual(product2.tenant, self.tenant1)
        self.assertEqual(product3.tenant, self.tenant2)
