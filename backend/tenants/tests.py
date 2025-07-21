from django.test import TestCase
from tenants.models import Tenant


class TenantCreationTest(TestCase):
    def test_create_tenant_with_name_and_subdomain(self):
        tenant = Tenant.objects.create(name="Alice's Shop", subdomain="alice")
        self.assertEqual(tenant.name, "Alice's Shop")
        self.assertEqual(tenant.subdomain, "alice")
