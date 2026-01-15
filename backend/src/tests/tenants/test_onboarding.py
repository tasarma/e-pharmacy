import pytest
from django.contrib.auth import get_user_model
from tenants.services import TenantOnboardingService
from tenants.models import Tenant, TenantSettings

User = get_user_model()


@pytest.mark.django_db
class TestTenantOnboarding:
    """Test tenant onboarding service."""

    def test_successful_onboarding(self):
        """Test complete tenant onboarding."""
        result = TenantOnboardingService.create_tenant_with_manager(
            name="New Pharmacy",
            subdomain="newpharm",
            manager_email="manager@newpharm.com",
            manager_password="StrongPass123!",
            manager_first_name="John",
            manager_last_name="Doe",
        )

        assert result["success"] is True
        assert result["tenant"].subdomain == "newpharm"
        assert result["manager_user"].email == "manager@newpharm.com"

        # Verify tenant created
        assert Tenant.objects.filter(subdomain="newpharm").exists()

        # Verify manager user created
        assert User.all_objects.filter(email="manager@newpharm.com").exists()

        # Verify settings created
        assert TenantSettings.objects.filter(tenant=result["tenant"]).exists()

    def test_onboarding_rollback_on_error(self):
        """Test onboarding rolls back on error."""
        initial_tenant_count = Tenant.objects.count()
        initial_user_count = User.all_objects.count()

        # Invalid subdomain should cause rollback
        with pytest.raises(Exception):
            TenantOnboardingService.create_tenant_with_manager(
                name="Test",
                subdomain="admin",  # Reserved
                manager_email="test@example.com",
                manager_password="TestPass123!",
            )

        # Nothing should be created
        assert Tenant.objects.count() == initial_tenant_count
        assert User.all_objects.count() == initial_user_count

    def test_duplicate_subdomain_fails(self, tenant):
        """Test onboarding fails with duplicate subdomain."""
        with pytest.raises(Exception):
            TenantOnboardingService.create_tenant_with_manager(
                name="Duplicate",
                subdomain=tenant.subdomain,
                manager_email="new@example.com",
                manager_password="TestPass123!",
            )
