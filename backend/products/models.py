from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q, CheckConstraint
from decimal import Decimal
import uuid

from tenants.models import TenantAwareModel, UniqueTenantConstraint
from .validators import validate_image_size


class Category(TenantAwareModel):
    """Product categories organized hierarchically."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)

    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    image = models.ImageField(
        upload_to="categories/%Y/%m/",  # MEDIA_ROOT/categories/2025/12/
        blank=True,
        null=True,
        validators=[validate_image_size],
    )

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)

    # Display
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["display_order", "name"]
        constraints = [
            UniqueTenantConstraint(fields=["slug"], name="unique_tenant_category_slug")
        ]
        indexes = [
            models.Index(fields=["tenant", "is_active", "display_order"]),
            models.Index(fields=["tenant", "parent"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Prevent circular parent relationships."""
        if self.parent:
            # Check for self-reference
            if self.parent == self:
                raise ValidationError("Category cannot be its own parent")

            # Check for circular reference
            parent = self.parent
            depth = 0
            MAX_DEPTH = 100

            while parent:
                depth += 1
                if parent == self:
                    raise ValidationError("Circular parent relationship detected")
                if depth > MAX_DEPTH:
                    raise ValidationError("Max category depth exceeded")
                parent = parent.parent

    def get_ancestors(self):
        """Get all parent categories."""
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.append(parent)
            parent = parent.parent
        return ancestors

    def get_descendants(self):
        """Get all child categories recursively."""
        # Optimization: Replace manual recursion in Category
        # with a specialized tree library like Treebeard
        # to avoid O(N) or O(N+1)
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants


class Product(TenantAwareModel):
    """Core product model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic Info
    name = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=300)
    sku = models.CharField(
        max_length=100, verbose_name="SKU", help_text="Stock Keeping Unit"
    )
    # barcode = models.CharField(max_length=100, blank=True)

    description = models.TextField()
    short_description = models.TextField(max_length=500, blank=True)

    # Categorization
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )

    # Pricing
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original price for showing discounts",
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost to tenant (for profit calculation)",
    )

    # Inventory
    track_inventory = models.BooleanField(default=True)  # False means infinite stock
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    low_stock_threshold = models.PositiveIntegerField(
        default=10, help_text="Alert when stock falls below this"
    )

    # Physical attributes
    weight = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, help_text="Weight in kg"
    )

    # Pharmaceutical specific (can be null for non-pharma)
    requires_prescription = models.BooleanField(default=False)
    active_ingredient = models.CharField(max_length=300, blank=True)
    dosage = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            UniqueTenantConstraint(fields=["sku"], name="unique_tenant_product_sku"),
            UniqueTenantConstraint(fields=["slug"], name="unique_tenant_product_slug"),
            CheckConstraint(
                condition=Q(stock_quantity__gte=0), name="stock_quantity_non_negative"
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "is_active", "category"]),
            models.Index(fields=["tenant", "is_featured"]),
            models.Index(fields=["tenant", "sku"]),
            models.Index(fields=["tenant", "name"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate product data."""
        if self.compare_at_price and self.compare_at_price <= self.price:
            raise ValidationError("Compare at price must be greater than regular price")

        if not self.track_inventory and self.stock_quantity > 0:
            raise ValidationError(
                "Cannot have stock quantity when not tracking inventory"
            )

    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        """Check if stock is below threshold."""
        if not self.track_inventory:
            return False
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def discount_percentage(self):
        """Calculate discount percentage."""
        if not self.compare_at_price:
            return 0
        return round(
            ((self.compare_at_price - self.price) / self.compare_at_price) * 100, 2
        )

    @property
    def profit_margin(self):
        """Calculate profit margin percentage."""
        if not self.cost_price or self.cost_price == 0:
            return None
        return round(((self.price - self.cost_price) / self.price) * 100, 2)

    def adjust_stock(self, quantity: int, reason: str = "", user=None):
        """
        Thread-safe stock adjustment using database locking.
        Positive for increase, negative for decrease.
        """
        if not self.track_inventory:
            return

        with transaction.atomic():
            # LOCK this row until the transaction finishes
            # This forces other requests to wait
            product_locked = Product.objects.select_for_update().get(id=self.id)

            new_quantity = product_locked.stock_quantity + quantity
            if new_quantity < 0:
                raise ValidationError(
                    f"Insufficient stock. Current: {product_locked.stock_quantity}"
                )

            product_locked.stock_quantity = new_quantity
            product_locked.save(update_fields=["stock_quantity", "updated_at"])

            self.stock_quantity = new_quantity

            # Log the change
            StockMovement.objects.create(
                product=product_locked,
                quantity_change=quantity,
                quantity_before=product_locked.stock_quantity - quantity,
                quantity_after=new_quantity,
                reason=reason,
                created_by=user,  # Pass the user if available
                tenant=self.tenant,
            )


class ProductImage(TenantAwareModel):
    """Product images with ordering."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to="products/%Y/%m/", validators=[validate_image_size]
    )  # MEDIA_ROOT/products/2025/12/
    alt_text = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "created_at"]
        indexes = [
            models.Index(fields=["tenant", "product", "display_order"]),
        ]

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        """Ensure only one primary image per product."""
        if self.is_primary:
            with transaction.atomic():
                ProductImage.objects.filter(
                    product=self.product, is_primary=True
                ).exclude(id=self.id).update(is_primary=False)
                super().save(*args, **kwargs)


class StockMovement(TenantAwareModel):
    """Track all stock changes for audit trail."""

    REASON_CHOICES = [
        ("sale", "Sale"),
        ("return", "Customer Return"),
        ("adjustment", "Manual Adjustment"),
        ("damage", "Damaged"),
        ("expired", "Expired"),
        ("restock", "Restocked"),
        ("transfer", "Transfer"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="stock_movements"
    )

    quantity_change = models.IntegerField(
        help_text="Positive for increase, negative for decrease"
    )
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()

    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    notes = models.TextField(blank=True)

    # Reference to related object (order, return, etc.)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.UUIDField(null=True, blank=True)

    created_by = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "product", "-created_at"]),
            models.Index(fields=["tenant", "reason"]),
        ]

    def __str__(self):
        sign = "+" if self.quantity_change >= 0 else ""
        return f"{self.product.name}: {sign}{self.quantity_change}"


class ProductTag(TenantAwareModel):
    """Tags for organizing and filtering products."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            UniqueTenantConstraint(fields=["slug"], name="unique_tenant_tag_slug")
        ]

    def __str__(self):
        return self.name


class ProductTagAssignment(TenantAwareModel):
    """Many-to-many relationship between products and tags."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="tag_assignments"
    )
    tag = models.ForeignKey(
        ProductTag, on_delete=models.CASCADE, related_name="product_assignments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueTenantConstraint(
                fields=["product", "tag"], name="unique_tenant_product_tag"
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "product"]),
            models.Index(fields=["tenant", "tag"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.tag.name}"
