import pytest
from rest_framework.exceptions import ValidationError
from users.serializers import TenantAwareUserCreateSerializer, TenantAwareTokenObtainSerializer
from tenants.context import set_tenant_context
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestTenantAwareUserCreateSerializer:
    """Test user creation serializer."""
    
    def test_create_user_with_valid_data(self, tenant):
        """Test creating user with valid data."""
        with set_tenant_context(tenant=tenant):
            serializer = TenantAwareUserCreateSerializer(data={
                'email': 'newuser@test.com',
                'password': 'StrongPass123!'
            })
            
            assert serializer.is_valid()
            user = serializer.save()
            
            assert user.email == 'newuser@test.com'
            assert user.tenant == tenant
            assert user.role == 'user'
    
    def test_create_user_sets_role_to_user(self, tenant):
        """Test created user always has 'user' role."""
        with set_tenant_context(tenant=tenant):
            serializer = TenantAwareUserCreateSerializer(data={
                'email': 'role@test.com',
                'password': 'StrongPass123!',
                'role': 'admin'  # Should be ignored
            })
            
            assert serializer.is_valid()
            user = serializer.save()
            
            assert user.role == 'user'  # Forced to 'user'
    
    def test_create_user_without_tenant_context_fails(self):
        """Test creating user without tenant context fails."""
        serializer = TenantAwareUserCreateSerializer(data={
            'email': 'nocontext@test.com',
            'password': 'StrongPass123!'
        })
        
        assert serializer.is_valid()
        
        with pytest.raises(ValidationError) as exc:
            serializer.save()
        
        assert 'tenant' in str(exc.value).lower()
    
    def test_password_is_write_only(self, tenant):
        """Test password field is write-only."""
        with set_tenant_context(tenant=tenant):
            user = User.objects.create_user(
                email='writeonly@test.com',
                password='Pass123!',
                tenant=tenant
            )
            
            serializer = TenantAwareUserCreateSerializer(user)
            assert 'password' not in serializer.data


@pytest.mark.django_db
class TestTenantAwareTokenObtainSerializer:
    """Test JWT token serializer."""
    
    def test_validate_user_belongs_to_tenant(self, manager):
        """Test validation ensures user belongs to current tenant."""
        with set_tenant_context(tenant=manager.tenant):
            serializer = TenantAwareTokenObtainSerializer(data={
                'email': manager.email,
                'password': 'TestPass123!'
            })
            
            assert serializer.is_valid()
            validated_data = serializer.validated_data
            
            assert 'access' in validated_data
            assert 'refresh' in validated_data
    
    def test_validate_fails_for_wrong_tenant(self, manager, other_tenant):
        """Test validation fails when user doesn't belong to current tenant."""
        with set_tenant_context(tenant=other_tenant):
            serializer = TenantAwareTokenObtainSerializer(data={
                'email': manager.email,
                'password': 'TestPass123!'
            })
            
            # Should fail validation
            with pytest.raises(Exception):
                serializer.is_valid(raise_exception=True)
