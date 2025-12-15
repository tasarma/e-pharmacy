import pytest
from django.contrib.auth import authenticate, get_user_model
from django.test import RequestFactory
from tenants.context import set_tenant_context

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestTenantAwareAuthentication:
    """Test tenant-aware authentication backend."""

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    def test_authenticate_valid_user(self, manager, request_factory):
        """Test authenticating valid user in correct tenant."""
        request = request_factory.post("/login/")

        with set_tenant_context(tenant=manager.tenant):
            user = authenticate(
                request=request, username=manager.email, password="TestPass123!"
            )

        assert user is not None
        assert user == manager

    def test_authenticate_wrong_password(self, manager, request_factory):
        """Test authentication fails with wrong password."""
        request = request_factory.post("/login/")

        with set_tenant_context(tenant=manager.tenant):
            user = authenticate(
                request=request, username=manager.email, password="WrongPassword"
            )

        assert user is None

    def test_authenticate_nonexistent_user(self, tenant, request_factory):
        """Test authentication fails for non-existent user."""
        request = request_factory.post("/login/")

        with set_tenant_context(tenant=tenant):
            user = authenticate(
                request=request, username="nonexistent@test.com", password="Pass123!"
            )

        assert user is None

    def test_authenticate_user_in_different_tenant(
        self, manager, other_tenant, request_factory
    ):
        """Test cannot authenticate user from different tenant."""
        request = request_factory.post("/login/")

        # Try to authenticate in wrong tenant context
        with set_tenant_context(tenant=other_tenant):
            user = authenticate(
                request=request, username=manager.email, password="TestPass123!"
            )

        assert user is None

    def test_authenticate_same_email_different_tenants(
        self, tenant, other_tenant, request_factory
    ):
        """Test authenticating users with same email in different tenants."""
        email = "shared@test.com"
        password = "SharedPass123!"

        # Create user in first tenant
        with set_tenant_context(tenant=tenant):
            user1 = User.objects.create_user(
                email=email, password=password, tenant=tenant
            )

        # Create user with same email in second tenant
        with set_tenant_context(tenant=other_tenant):
            user2 = User.objects.create_user(
                email=email, password=password, tenant=other_tenant
            )

        request = request_factory.post("/login/")

        # Authenticate in first tenant
        with set_tenant_context(tenant=tenant):
            authenticated_user = authenticate(
                request=request, username=email, password=password
            )
            assert authenticated_user == user1

        # Authenticate in second tenant
        with set_tenant_context(tenant=other_tenant):
            authenticated_user = authenticate(
                request=request, username=email, password=password
            )
            assert authenticated_user == user2

    def test_authenticate_inactive_user(self, tenant, request_factory):
        """Test cannot authenticate inactive user."""
        with set_tenant_context(tenant=tenant):
            user = User.objects.create_user(
                email="inactive@test.com",
                password="Pass123!",
                tenant=tenant,
                is_active=False,
            )

        request = request_factory.post("/login/")

        with set_tenant_context(tenant=tenant):
            authenticated_user = authenticate(
                request=request, username=user.email, password="Pass123!"
            )

        assert authenticated_user is None

    def test_get_user_respects_tenant(self, manager):
        """Test get_user returns user only in correct tenant context."""
        from users.backends import TenantAwareAuthBackend

        backend = TenantAwareAuthBackend()

        # Get user in correct tenant
        with set_tenant_context(tenant=manager.tenant):
            user = backend.get_user(manager.id)
            assert user == manager

        # Try to get user in different tenant
        with pytest.raises(Exception):
            with set_tenant_context(tenant=None):
                user = backend.get_user(manager.id)
