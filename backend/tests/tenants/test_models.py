import pytest
from django.core.exceptions import ValidationError
from tenants.models import Tenant, TenantSettings
from tenants.context import set_tenant_context, tenant_context_disabled


@pytest.mark.django_db
class TestTenantModel:
    """Test Tenant model validation and behavior."""
    
    def test_create_valid_tenant(self):
        """Test creating tenant with valid data."""
        with tenant_context_disabled():
            tenant = Tenant.objects.create(
                name="Valid Pharmacy",
                subdomain="validpharm"
            )
        
        assert tenant.id is not None
        assert tenant.active is False
        assert str(tenant) == "Valid Pharmacy (validpharm)"
    
    def test_subdomain_validation_invalid_chars(self):
        """Test subdomain rejects invalid characters."""
        with tenant_context_disabled():
            tenant = Tenant(
                name="Test",
                subdomain="test_invalid!"
            )

            with pytest.raises(ValidationError) as exc:
                tenant.full_clean()

            assert "subdomain" in str(exc.value).lower()

    def test_subdomain_reserved_keywords(self):
        """Test subdomain rejects reserved keywords."""
        with tenant_context_disabled():
            tenant = Tenant(
                name="Admin Store",
                subdomain="admin"
            )

            with pytest.raises(ValidationError) as exc:
                tenant.save()

            assert "reserved" in str(exc.value).lower()

    def test_subdomain_uniqueness(self, tenant):
        """Test subdomain must be unique."""
        with tenant_context_disabled():
            duplicate = Tenant(
                name="Duplicate",
                subdomain=tenant.subdomain
            )

            with pytest.raises(ValidationError):
                duplicate.full_clean()


@pytest.mark.django_db
class TestTenantSettings:
    """Test TenantSettings model."""
    
    def test_create_settings(self, tenant):
        """Test creating tenant settings."""
        with set_tenant_context(tenant=tenant):
            settings = TenantSettings.objects.create(
                tenant=tenant,
                store_name="My Store",
                email="store@example.com"
            )
        
        assert settings.tenant == tenant
        assert settings.store_name == "My Store"
    
    def test_settings_one_to_one(self, tenant):
        """Test only one settings per tenant."""
        with set_tenant_context(tenant=tenant):
            TenantSettings.objects.create(
                tenant=tenant,
                store_name="Store 1",
                email="store1@example.com"
            )

            # Attempt to create duplicate
            with pytest.raises(Exception):
                TenantSettings.objects.create(
                    tenant=tenant,
                    store_name="Store 2",
                    email="store2@example.com"
                )

    def test_full_address(self, tenant_settings):
        """Test full address formatting."""
        tenant_settings.address_line1 = "123 Main St"
        tenant_settings.city = "Boston"
        tenant_settings.state_province = "MA"
        tenant_settings.postal_code = "02101"
        tenant_settings.country = "USA"
        tenant_settings.save()

        address = tenant_settings.get_full_address()
        assert "123 Main St" in address
        assert "Boston" in address
        assert "MA" in address


@pytest.mark.django_db
class TestTenantIsolation:
    """Test tenant data isolation."""
    
    def test_users_isolated_by_tenant(self, manager, other_tenant_user):
        """Test users from different tenants are isolated."""
        with set_tenant_context(tenant=manager.tenant):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Should only see users from current tenant
            users = User.objects.all()
            assert manager in users
            assert other_tenant_user not in users

    def test_all_objects_bypasses_tenant_filter(self, manager, other_tenant_user):
        """Test all_objects manager sees all users."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        with set_tenant_context(tenant=manager.tenant):
            # all_objects should bypass tenant filtering
            all_users = User.all_objects.all()
            assert manager in all_users
            assert other_tenant_user in all_users

    def test_cannot_access_other_tenant_data(self, tenant, other_tenant):
        """Test cannot access data from different tenant."""
        from users.models import UserProfile
        
        # Create profile in first tenant
        with set_tenant_context(tenant=tenant):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            user1 = User.objects.create_user(
                email="test1@example.com",
                password="test123",
                first_name="John",
                tenant=tenant
            )
            profile1 = UserProfile.objects.get(
                user=user1
            )
        
        # Try to access from second tenant
        with set_tenant_context(tenant=other_tenant):
            profiles = UserProfile.objects.all()
            assert profile1 not in profiles
            assert not profiles.filter(id=profile1.id).exists()
