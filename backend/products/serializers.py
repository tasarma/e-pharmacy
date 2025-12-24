from rest_framework import serializers
from django.utils.text import slugify

from .models import Category, Product


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
