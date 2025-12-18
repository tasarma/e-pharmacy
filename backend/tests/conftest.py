import pytest
from django.contrib.auth import get_user_model
from tenants.models import Tenant, TenantSettings
from tenants.context import set_tenant_context, tenant_context_disabled
from django.core.cache import cache

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    """
    Clear the cache before (and/or after) each test to prevent 
    stale tenant objects from persisting across DB rollbacks.
    """
    cache.clear()
    yield
    cache.clear()

@pytest.fixture
def tenant(db):
    """Create a test tenant."""
    with tenant_context_disabled():
        tenant = Tenant.objects.create(
            name="Test Pharmacy", subdomain="testpharm", active=True
        )
    return tenant


@pytest.fixture
def inactive_tenant(db):
    """Create an inactive tenant."""
    with tenant_context_disabled():
        tenant = Tenant.objects.create(
            name="Inactive Pharmacy", subdomain="inactive", active=False
        )
    return tenant


@pytest.fixture
def tenant_settings(db, tenant):
    """Create tenant settings."""
    with set_tenant_context(tenant=tenant):
        settings, created = TenantSettings.objects.get_or_create(
            tenant=tenant,
            defaults={
                "store_name": "Test Pharmacy Store",
                "email": "test@testpharm.com",
                "phone_number": "+1234567890",
            },
        )
    return settings


@pytest.fixture
def manager(db, tenant):
    """Create manager user for tenant."""
    with set_tenant_context(tenant=tenant):
        user = User.objects.create_user(
            email="manager@testpharm.com",
            password="TestPass123!",
            role="manager",
            is_staff=True,
            tenant=tenant,
        )
    return user


@pytest.fixture
def regular_user(db, tenant):
    """Create regular user for tenant."""
    with set_tenant_context(tenant=tenant):
        user = User.objects.create_user(
            email="user@gmail.com",
            password="TestPass123!",
            role="user",
            tenant=tenant,
        )
    return user


@pytest.fixture
def other_tenant(db):
    """Create second tenant for isolation tests."""
    with tenant_context_disabled():
        tenant = Tenant.objects.create(
            name="Other Pharmacy", subdomain="otherpharm", active=True
        )
    return tenant


@pytest.fixture
def other_tenant_user(db, other_tenant):
    """Create user in different tenant."""
    with set_tenant_context(tenant=other_tenant):
        user = User.objects.create_user(
            email="user@gmail.com",
            password="TestPass123!",
            role="user",
            tenant=other_tenant,
        )
    return user


@pytest.fixture
def client():
    """Return DRF API client."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def category(db, tenant):
    return Category.objects.create(
        tenant=tenant,
        name="Test Category",
        slug="test-category"
    )
