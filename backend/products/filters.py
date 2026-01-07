from django_filters import rest_framework as filters
from .models import Product


class ProductFilter(filters.FilterSet):
    """Advanced filtering for products."""
    
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    category = filters.UUIDFilter(field_name='category__id')
    category_slug = filters.CharFilter(field_name='category__slug')
    
    in_stock = filters.BooleanFilter(method='filter_in_stock')
    is_featured = filters.BooleanFilter()
    is_active = filters.BooleanFilter()
    
    requires_prescription = filters.BooleanFilter()
    
    class Meta:
        model = Product
        fields = [
            'category', 'is_featured', 'is_active',
            'requires_prescription'
        ]
    
    def filter_in_stock(self, queryset, name, value):
        """Filter by stock availability."""
        if value:
            return queryset.filter(
                track_inventory=False
            ) | queryset.filter(
                track_inventory=True,
                stock_quantity__gt=0
            )
        else:
            return queryset.filter(
                track_inventory=True,
                stock_quantity=0
            )
