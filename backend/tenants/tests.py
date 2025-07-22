from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from tenants.models import Tenant


class TenantModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@gmail.com', password='123')

    def test_tenant_can_be_created_with_required_fields(self):
        tenant = Tenant.objects.create(
            name="Alice's Shop",
            subdomain="alice",
            owner=self.user,
            active=True,
        )
        self.assertEqual(tenant.name, "Alice's Shop")
        self.assertEqual(tenant.subdomain, "alice")
        self.assertEqual(tenant.owner, self.user)
        self.assertTrue(tenant.active)
        self.assertIsNotNone(tenant.created_at)

    def test_tenant_subdomain_must_be_unique(self):
        Tenant.objects.create(name="Alice's Shop", subdomain="alice")
        with self.assertRaises(ValidationError):
            duplicate_tenant = Tenant(name="Another Shop", subdomain="alice")
            duplicate_tenant.full_clean()  # This triggers model validation
