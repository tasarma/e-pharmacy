import pytest
from django.contrib.auth import get_user_model
from users.models import UserProfile
from tenants.context import set_tenant_context

User = get_user_model()


@pytest.mark.django_db
class TestUserSignals:
    """Test user-related signals."""
    
    def test_profile_created_on_user_save(self, tenant):
        """Test profile is automatically created when user is created."""
        with set_tenant_context(tenant=tenant):
            user = User.objects.create_user(
                email="signal@test.com",
                password="Pass123!",
                tenant=tenant
            )
        
        # Profile should be auto-created
        assert hasattr(user, 'profile')
        with set_tenant_context(tenant=tenant):
            assert UserProfile.objects.filter(user=user).exists()
    
    def test_profile_not_duplicated_on_update(self, manager):
        """Test profile is not duplicated when user is updated."""
        original_profile = manager.profile
        
        with set_tenant_context(tenant=manager.tenant):
            manager.first_name = "Updated"
            manager.save()
        
        # Should still have only one profile
        with set_tenant_context(tenant=manager.tenant):
            assert UserProfile.objects.filter(user=manager).count() == 1
        assert manager.profile == original_profile
    
    def test_profile_deleted_with_user(self, tenant):
        """Test profile is deleted when user is deleted."""
        with set_tenant_context(tenant=tenant):
            user = User.objects.create_user(
                email="delete@test.com",
                password="Pass123!",
                tenant=tenant
            )
            profile_id = user.profile.id
            
            user.delete()
        
        # Profile should be deleted
        with set_tenant_context(tenant=tenant):
            assert not UserProfile.objects.filter(id=profile_id).exists()
    
    def test_profile_saved_with_user(self, manager):
        """Test profile is saved when user is saved (if it exists)."""
        profile = manager.profile
        profile.first_name = "Test"
        
        with set_tenant_context(tenant=manager.tenant):
            manager.save()
        
        profile.refresh_from_db()
        # Signal should have triggered profile.save()
        assert profile.first_name == "Test"
