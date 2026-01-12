import pytest
from django.contrib.auth import get_user_model

from tenants.context import set_tenant_context
from decimal import Decimal
from products.models import Category, Product, ProductTag


User = get_user_model()


@pytest.fixture
def category(db, tenant):
    """Create a test category."""
    with set_tenant_context(tenant=tenant):
        category = Category.objects.create(
            name="Test Category",
            slug="test-category",
            description="Test category description",
            is_active=True,
            display_order=1,
        )
    return category


@pytest.fixture
def parent_category(db, tenant):
    """Create a parent category."""
    with set_tenant_context(tenant=tenant):
        category = Category.objects.create(
            name="Parent Category", slug="parent-category", is_active=True
        )
    return category


@pytest.fixture
def child_category(db, tenant, parent_category):
    """Create a child category."""
    with set_tenant_context(tenant=tenant):
        category = Category.objects.create(
            name="Child Category",
            slug="child-category",
            parent=parent_category,
            is_active=True,
        )
    return category


@pytest.fixture
def product(db, tenant, category):
    """Create a test product."""
    with set_tenant_context(tenant=tenant):
        product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            sku="TEST-001",
            description="Test product description",
            short_description="Short description",
            category=category,
            price=Decimal("99.99"),
            compare_at_price=Decimal("149.99"),
            cost_price=Decimal("50.00"),
            track_inventory=True,
            stock_quantity=100,
            low_stock_threshold=10,
            is_active=True,
        )
    return product


@pytest.fixture
def product_no_inventory(db, tenant, category):
    """Create product that doesn't track inventory."""
    with set_tenant_context(tenant=tenant):
        product = Product.objects.create(
            name="Digital Product",
            slug="digital-product",
            sku="DIG-001",
            description="Digital product",
            category=category,
            price=Decimal("29.99"),
            track_inventory=False,
            stock_quantity=0,
            is_active=True,
        )
    return product


@pytest.fixture
def low_stock_product(db, tenant, category):
    """Create a low stock product."""
    with set_tenant_context(tenant=tenant):
        product = Product.objects.create(
            name="Low Stock Product",
            slug="low-stock",
            sku="LOW-001",
            description="Low stock",
            category=category,
            price=Decimal("19.99"),
            track_inventory=True,
            stock_quantity=5,
            low_stock_threshold=10,
            is_active=True,
        )
    return product


@pytest.fixture
def out_of_stock_product(db, tenant, category):
    """Create an out of stock product."""
    with set_tenant_context(tenant=tenant):
        product = Product.objects.create(
            name="Out of Stock",
            slug="out-of-stock",
            sku="OUT-001",
            description="Out of stock",
            category=category,
            price=Decimal("39.99"),
            track_inventory=True,
            stock_quantity=0,
            is_active=True,
        )
    return product


@pytest.fixture
def product_tag(db, tenant):
    """Create a product tag."""
    with set_tenant_context(tenant=tenant):
        tag = ProductTag.objects.create(name="Test Tag", slug="test-tag")
    return tag
