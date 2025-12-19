import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from users.models import UserProfile
from tenants.context import set_tenant_context, tenant_context_disabled

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserModel:
    """Test CustomUser model."""

    def test_create_user_with_email(self, tenant):
        """Test creating user with email."""
        with set_tenant_context(tenant=tenant):
            user = User.objects.create_user(
                email="test@example.com", password="TestPass123!", tenant=tenant
            )

        assert user.email == "test@example.com"
        assert user.check_password("TestPass123!")
        assert user.tenant == tenant
        assert user.is_active is True
        assert user.is_staff is False

    def test_create_user_without_email_fails(self, tenant):
        """Test creating user without email raises error."""
        with set_tenant_context(tenant=tenant):
            with pytest.raises(ValueError) as exc:
                User.objects.create_user(email="", password="TestPass123!")

            assert "email" in str(exc.value).lower()

    def test_create_superuser(self):
        """Test creating superuser."""
        with tenant_context_disabled():
            user = User.all_objects.create_superuser(
                email="admin@example.com", password="AdminPass123!"
            )

        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.role == "admin"

    def test_email_case_normalization(self, tenant):
        """Test email is normalized to lowercase."""
        with set_tenant_context(tenant=tenant):
            user = User.objects.create_user(
                email="Test@Example.COM", password="TestPass123!", tenant=tenant
            )

        # Django's normalize_email lowercases domain only
        assert user.email == "Test@example.com"

    def test_duplicate_email_same_tenant_fails(self, tenant, manager):
        """Test duplicate email in same tenant fails."""
        with set_tenant_context(tenant=tenant):
            with pytest.raises(ValidationError):
                user = User(email=manager.email, tenant=tenant)
                user.full_clean()

    def test_duplicate_email_different_tenant_succeeds(self, tenant, other_tenant):
        """Test same email in different tenants is allowed."""
        email = "shared@example.com"

        with set_tenant_context(tenant=tenant):
            user1 = User.objects.create_user(
                email=email, password="Pass123!", tenant=tenant
            )

        with set_tenant_context(tenant=other_tenant):
            user2 = User.objects.create_user(
                email=email, password="Pass123!", tenant=other_tenant
            )

        assert user1.email == user2.email
        assert user1.tenant != user2.tenant

    def test_user_roles(self, tenant):
        """Test different user roles."""
        with set_tenant_context(tenant=tenant):
            admin = User.objects.create_user(
                email="admin@test.com", password="Pass123!", role="admin", tenant=tenant
            )
            manager = User.objects.create_user(
                email="manager@test.com",
                password="Pass123!",
                role="manager",
                tenant=tenant,
            )
            user = User.objects.create_user(
                email="user@test.com", password="Pass123!", role="user", tenant=tenant
            )

        assert admin.role == "admin"
        assert manager.role == "manager"
        assert user.role == "user"


@pytest.mark.django_db
class TestUserProfile:
    """Test UserProfile model."""

    def test_profile_created_on_user_creation(self, tenant):
        """Test profile is auto-created when user is created."""
        with set_tenant_context(tenant=tenant):
            user = User.objects.create_user(
                email="newuser@test.com", password="Pass123!", tenant=tenant
            )

        assert hasattr(user, "profile")
        assert user.profile.tenant == tenant

    def test_profile_one_to_one_relationship(self, manager):
        """Test profile has one-to-one relationship with user."""
        profile = manager.profile

        assert profile.user == manager
        assert profile.tenant == manager.tenant

    def test_update_profile_fields(self, manager):
        """Test updating profile fields."""
        profile = manager.profile

        with set_tenant_context(tenant=manager.tenant):
            profile.first_name = "John"
            profile.last_name = "Doe"
            profile.phone_number = "+1234567890"
            profile.address = "123 Main St"
            profile.save()

        profile.refresh_from_db()
        assert profile.first_name == "John"
        assert profile.last_name == "Doe"
        assert profile.phone_number == "+1234567890"

    def test_display_name_without_names(self, manager):
        """Test display name falls back to email."""
        profile = manager.profile
        profile.first_name = ""
        profile.last_name = ""

        assert profile.display_name == manager.email

    def test_profile_isolated_by_tenant(self, manager, other_tenant_user):
        """Test profiles are isolated by tenant."""
        with set_tenant_context(tenant=manager.tenant):
            profiles = UserProfile.objects.all()

            assert manager.profile in profiles
            assert other_tenant_user.profile not in profiles

    def test_duplicate_user_profile_same_tenant_fails(self, manager):
        """Test cannot create duplicate profile for same user in tenant."""
        with set_tenant_context(tenant=manager.tenant):
            with pytest.raises(Exception):
                UserProfile.objects.create(user=manager, tenant=manager.tenant)

    def test_profile_cascade_delete(self, tenant):
        """Test profile is deleted when user is deleted."""
        with set_tenant_context(tenant=tenant):
            user = User.objects.create_user(
                email="delete@test.com", password="Pass123!", tenant=tenant
            )
            profile_id = user.profile.id

        with set_tenant_context(tenant=tenant):
            user.delete()

            # Profile should be deleted
            assert not UserProfile.objects.filter(id=profile_id).exists()


@pytest.mark.django_db
class TestUserManager:
    """Test TenantAwareUserManager."""

    def test_queryset_filtered_by_tenant(self, manager, other_tenant_user):
        """Test manager filters users by current tenant."""
        with set_tenant_context(tenant=manager.tenant):
            users = User.objects.all()

            assert users.filter(id=manager.id).exists()
            assert not users.filter(id=other_tenant_user.id).exists()

    def test_all_objects_bypasses_filter(self, manager, other_tenant_user):
        """Test all_objects admin sees all users."""
        all_users = User.all_objects.all()

        assert all_users.filter(id=manager.id).exists()
        assert all_users.filter(id=other_tenant_user.id).exists()

    def test_create_user_sets_tenant_from_context(self, tenant):
        """Test create_user automatically sets tenant from context."""
        with set_tenant_context(tenant=tenant):
            user = User.objects.create_user(email="auto@test.com", password="Pass123!")

        assert user.tenant == tenant

    def test_get_by_email_respects_tenant(self, manager, other_tenant):
        """Test getting user by email respects tenant context."""
        # Create user with same email in different tenant
        with set_tenant_context(tenant=other_tenant):
            other_user = User.objects.create_user(
                email=manager.email, password="Pass123!", tenant=other_tenant
            )

        # Query from first tenant
        with set_tenant_context(tenant=manager.tenant):
            user = User.objects.get(email=manager.email)
            assert user.id == manager.id
            assert user.tenant == manager.tenant

        # Query from second tenant
        with set_tenant_context(tenant=other_tenant):
            user = User.objects.get(email=manager.email)
            assert user.id == other_user.id
            assert user.tenant == other_tenant


@pytest.mark.django_db
class TestUserConstraints:
    """Test user model constraints."""

    def test_unique_tenant_email_constraint(self, tenant):
        """Test email must be unique per tenant."""
        with set_tenant_context(tenant=tenant):
            User.objects.create_user(
                email="unique@test.com", password="Pass123!", tenant=tenant
            )

            # Attempt duplicate
            with pytest.raises(Exception):
                User.objects.create_user(
                    email="unique@test.com", password="Pass123!", tenant=tenant
                )

    def test_user_profile_unique_constraint(self, manager):
        """Test one profile per user per tenant."""
        with set_tenant_context(tenant=manager.tenant):
            # Profile already exists from signal
            assert UserProfile.objects.filter(user=manager).count() == 1

            # Attempt to create duplicate
            with pytest.raises(Exception):
                UserProfile.objects.create(
                    user=manager, tenant=manager.tenant, first_name="Duplicate"
                )
