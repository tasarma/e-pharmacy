from rest_framework import serializers
from django.utils.text import slugify

from .models import (
    Category,
    Product,
    ProductTag,
    ProductImage,
    StockMovement,
)


class AbsoluteImageField(serializers.ReadOnlyField):
    """Custom field to handle absolute URLs"""

    def to_representation(self, value):
        if not value:
            return None
        request = self.context.get("request")
        try:
            url = value.url
            return request.build_absolute_uri(url)
        except (AttributeError, ValueError):
            return None


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer with parent relationship."""

    parent_name = serializers.CharField(source="parent.name", read_only=True)
    children_count = serializers.IntegerField(
        source="active_children_count", read_only=True
    )
    products_count = serializers.IntegerField(
        source="active_products_count", read_only=True
    )
    image_url = AbsoluteImageField(source="image")

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "parent_name",
            "children_count",
            "products_count",
            "image",
            "image_url",
            "meta_title",
            "meta_description",
            "is_active",
            "display_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_slug(self, value):
        """Ensure slug is URL-safe."""
        if not value:
            return slugify(self.initial_data.get("name", ""))
        return slugify(value)


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    primary_image = serializers.SerializerMethodField()
    in_stock = serializers.BooleanField(source="is_in_stock", read_only=True)
    discount_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "category",
            "category_name",
            "price",
            "compare_at_price",
            "discount_percentage",
            "short_description",
            "primary_image",
            "in_stock",
            "stock_quantity",
            "is_featured",
            "is_active",
            "requires_prescription",
            "created_at",
        ]

    def get_primary_image(self, obj):
        primary_imgs = getattr(obj, "primary_img", [])
        if primary_imgs:
            img_obj = primary_imgs[0]
            request = self.context.get("request")
            if request and img_obj.image:
                return request.build_absolute_uri(img_obj.image.url)
            return img_obj.image.url if img_obj.image else None
        return None


class ProductImageSerializer(serializers.ModelSerializer):
    """Product image serializer using custom field for efficiency."""

    image_url = AbsoluteImageField(source="image")

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "image_url",
            "alt_text",
            "display_order",
            "is_primary",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed product serializer with optimized tag and image handling."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()
    is_in_stock = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "description",
            "short_description",
            "category",
            "category_name",
            "price",
            "compare_at_price",
            "cost_price",
            "discount_percentage",
            "profit_margin",
            "track_inventory",
            "stock_quantity",
            "low_stock_threshold",
            "is_in_stock",
            "is_low_stock",
            "weight",
            "requires_prescription",
            "active_ingredient",
            "dosage",
            "manufacturer",
            "meta_title",
            "meta_description",
            "is_active",
            "is_featured",
            "images",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_tags(self, obj):
        # Uses prefetch_related('tag_assignments__tag') from ViewSet
        return [
            {
                "id": str(assignment.tag.id),
                "name": assignment.tag.name,
                "slug": assignment.tag.slug,
            }
            for assignment in obj.tag_assignments.all()
        ]


class StockAdjustmentSerializer(serializers.Serializer):
    """Serializer for manual stock adjustments."""

    quantity = serializers.IntegerField()
    reason = serializers.ChoiceField(choices=StockMovement.REASON_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError("Quantity cannot be zero")
        return value


class StockMovementSerializer(serializers.ModelSerializer):
    """Stock movement history serializer."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    created_by_email = serializers.CharField(
        source="created_by.email", read_only=True, allow_null=True
    )

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity_change",
            "quantity_before",
            "quantity_after",
            "reason",
            "notes",
            "reference_type",
            "reference_id",
            "created_by",
            "created_by_email",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "quantity_before",
            "quantity_after",
            "created_by",
            "created_at",
        ]


class ProductTagSerializer(serializers.ModelSerializer):
    """Product tag serializer."""

    class Meta:
        model = ProductTag
        fields = ["id", "name", "slug", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_slug(self, value):
        if not value:
            return slugify(self.initial_data.get("name", ""))
        return slugify(value)
