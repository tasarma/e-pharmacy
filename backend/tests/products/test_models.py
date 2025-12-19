import pytest
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import connections, DatabaseError

from products.models import Product, Category
from tenants.context import set_tenant_context
from tenants.exceptions import TenantError

import structlog

logger = structlog.get_logger(__name__)

# --- CONCURRENCY TEST ---


@pytest.mark.django_db(transaction=True)
def test_product_stock_concurrency(tenant, category):
    """
    Test that 5 threads trying to buy the last item results in
    exactly 1 success and 4 failures.

    We use transaction=True to ensure real database commits occur,
    allowing select_for_update to actually lock rows across threads.
    """
    # 1. Setup: Create a product with exactly 1 item in stock
    with set_tenant_context(tenant=tenant):
        product = Product.objects.create(
            tenant=tenant,
            category=category,
            name="Hot Item",
            slug="hot-item",
            price=Decimal("10.00"),
            track_inventory=True,
            stock_quantity=1,  # Only 1 available!
        )

    # 2. Define the function that each thread will execute
    def attempt_purchase(thread_id):
        # CRITICAL: Manually set the context inside the new thread's scope
        with set_tenant_context(tenant=tenant):
            for conn in connections.all():
                conn.close_if_unusable_or_obsolete()

            try:
                # Re-fetch the product inside this thread's transaction
                p = Product.objects.get(id=product.id)
                p.adjust_stock(-1, reason=f"Thread-{thread_id}")
                return "success"
            except (ValidationError, TenantError):
                return "failed"
            except DatabaseError as e:
                # SQLite specific: Since SQLite uses database-level locking, concurrent
                # threads often hit a 'database is locked' error immediately rather than
                # waiting for the lock to release (standard Row-Level Locking in Postgres).
                # We treat this as a 'failed' purchase attempt for the sake of the test.
                if "locked" in str(e).lower():
                    return "failed"
                return f"error: {str(e)}"

    # 3. Spin up 5 concurrent threads
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit 5 tasks
        futures = [executor.submit(attempt_purchase, i) for i in range(5)]
        # Collect results
        results = [f.result() for f in futures]

    # 4. Assertions
    success_count = results.count("success")
    fail_count = results.count("failed")

    # Reload product to check final state
    product.refresh_from_db()

    assert success_count == 1, "Only one thread should have succeeded"
    assert fail_count == 4, "4 threads should have failed due to insufficient stock"
    assert product.stock_quantity == 0, "Stock should be exactly 0"


# --- CIRCULAR DEPENDENCY TEST ---


@pytest.mark.django_db
def test_category_circular_dependency(tenant):
    """
    Test a complex circular dependency chain: A -> B -> C -> A
    """

    # 1. Create the chain (A -> B -> C)
    with set_tenant_context(tenant=tenant):
        cat_a = Category.objects.create(tenant=tenant, name="Category A", slug="cat-a")

        cat_b = Category.objects.create(
            tenant=tenant, name="Category B", slug="cat-b", parent=cat_a
        )

        cat_c = Category.objects.create(
            tenant=tenant, name="Category C", slug="cat-c", parent=cat_b
        )

    # Verify initial structure is valid
    cat_a.clean()  # Should pass

    # 2. Create the circle (Set A's parent to C)
    cat_a.parent = cat_c

    # 3. Assert that clean() raises ValidationError
    with pytest.raises(ValidationError) as exc_info:
        cat_a.clean()

    assert "Circular parent relationship detected" in str(exc_info.value)


@pytest.mark.django_db
def test_category_self_reference(tenant):
    """
    Simple test: A -> A
    """
    with set_tenant_context(tenant=tenant):
        cat_a = Category.objects.create(tenant=tenant, name="Category A", slug="cat-a")
        cat_a.parent = cat_a

    with pytest.raises(ValidationError) as exc_info:
        cat_a.clean()

    assert "Category cannot be its own parent" in str(exc_info.value)
