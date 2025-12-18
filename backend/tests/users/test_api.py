import pytest
from django.contrib.auth import get_user_model
import structlog

User = get_user_model()

logger = structlog.get_logger(__name__)

@pytest.mark.django_db(transaction=True)
class TestUserRegistration:
    """Test user registration endpoints."""

    def test_register_user_success(self, client, tenant):
        """Test successful user registration."""
        email = "newuser@test.com"
        
        
        response = client.post(
            "/auth/users/",
            {"email": email, "password": "StrongPass123!"},
            content_type="application/json",
            HTTP_HOST=f"{tenant.subdomain}.example.com",
        )

        assert response.status_code == 201
        
        from tenants.context import set_tenant_context
        # Verify the user exists in the correct tenant
        # (We need to verify the context to query the global/tenant specific user table properly)
        with set_tenant_context(tenant=tenant):
             assert User.objects.filter(email=email).exists()


    def test_register_duplicate_email_same_tenant(self, client, manager):
        """Test registering duplicate email in same tenant fails."""
        response = client.post(
            "/auth/users/",
            {"email": manager.email, "password": "Pass123!"},
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 400

    def test_register_weak_password_fails(self, client, tenant):
        """Test registration fails with weak password."""
        response = client.post(
            "/auth/users/",
            {"email": "weak@test.com", "password": "123"},
            HTTP_HOST=f"{tenant.subdomain}.example.com",
        )

        assert response.status_code == 400


@pytest.mark.django_db(transaction=True)
class TestUserLogin:
    """Test user login endpoints."""

    def test_login_success(self, client, regular_user):
        """Test successful login."""
        
        response = client.post(
            '/auth/jwt/create/',
            {
                'email': regular_user.email,
                'password': 'TestPass123!'
            },
            content_type="application/json",
            HTTP_HOST=f"{regular_user.tenant.subdomain}.example.com"
        )

        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_wrong_password(self, client, manager):
        """Test login fails with wrong password."""
        response = client.post(
            "/auth/jwt/create/",
            {"email": manager.email, "password": "WrongPassword"},
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client, tenant):
        """Test login fails for non-existent user."""
        response = client.post(
            "/auth/jwt/create/",
            {"email": "nonexistent@test.com", "password": "Pass123!"},
            HTTP_HOST=f"{tenant.subdomain}.example.com",
        )

        assert response.status_code == 401


# @pytest.mark.django_db(transaction=True)
@pytest.mark.django_db
class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_own_profile(self, client, manager):
        """Test user can get their own profile."""
        client.force_authenticate(user=manager)

        response = client.get(
            "/auth/users/me/", HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
        )

        assert response.status_code == 200
        assert response.data["email"] == manager.email

    def test_update_own_profile(self, client, manager):
        """Test user can update their own profile."""
        client.force_authenticate(user=manager)

        response = client.patch(
            "/auth/users/me/",
            {"first_name": "Updated"},
            HTTP_HOST=f"{manager.tenant.subdomain}.example.com",
        )

        assert response.status_code == 200

    def test_unauthenticated_cannot_access_profile(self, client, manager):
        """Test unauthenticated user cannot access profile."""
        response = client.get(
            "/auth/users/me/", HTTP_HOST=f"{manager.tenant.subdomain}.example.com"
        )

        assert response.status_code == 401
