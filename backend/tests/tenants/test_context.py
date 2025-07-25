from django.test import TestCase
from tenants.models import Tenant
from tenants import context
from tenants.exceptions import TenantError


class TestTenantContextState(TestCase):
    """Tests for tenant context state management."""

    def setUp(self):
        """Create tenants used in multiple tests."""
        self.tenant1 = Tenant.objects.create(name="Tenant One", subdomain="tenant1")
        self.tenant2 = Tenant.objects.create(name="Tenant Two", subdomain="tenant2")

    def test_default_state(self):
        # Act
        state = context.get_state()

        # Assert
        self.assertTrue(state["enabled"])
        self.assertIsNone(state["tenant"])

    def test_state_returns_value_from_contextvar(self):
        # Arrange
        test_state = {"enabled": False, "tenant": None}
        token = context.state.set(test_state)

        try:
            # Act
            state = context.get_state()

            # Assert
            self.assertEqual(state, test_state)
        finally:
            # Cleanup
            context.state.reset(token)

    def test_get_current_tenant_raises_when_none_set(self):
        # Act & Assert
        with self.assertRaises(TenantError) as cm:
            context.get_current_tenant()

        self.assertIn("Tenant is required", str(cm.exception))

    def test_set_and_get_current_tenant(self):
        # Arrange
        tenant = self.tenant1

        # Act
        with context.set_tenant_context(tenant):
            current_tenant = context.get_current_tenant()

            # Assert
            self.assertEqual(current_tenant, tenant)

    def test_nested_tenant_contexts_restore_previous_tenant(self):
        # Arrange
        tenant1 = self.tenant1
        tenant2 = self.tenant2

        # Act
        with context.set_tenant_context(tenant1):
            first_level_tenant = context.get_current_tenant()

            with context.set_tenant_context(tenant2):
                second_level_tenant = context.get_current_tenant()

            restored_tenant = context.get_current_tenant()

        # Assert
        self.assertEqual(first_level_tenant, tenant1)
        self.assertEqual(second_level_tenant, tenant2)
        self.assertEqual(restored_tenant, tenant1)
        self.assertIsNone(context.get_state()["tenant"])

    def test_tenant_context_can_be_disabled(self):
        # Act
        with context.tenant_context_disabled():
            tenant = context.get_current_tenant()

            # Assert
            self.assertIsNone(tenant)
