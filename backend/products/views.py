from django.db.models import Count, Q, Prefetch
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import structlog

from .models import Category, Product
from .serializers import CategorySerializer, ProductListSerializer
from .permissions import IsStaffOrReadOnly

logger = structlog.get_logger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for product categories.
    Manager and Super Admin can create/update, all authenticated users can read.
    """

    serializer_class = [CategorySerializer]
    permission_class = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "display_order", "created_at"]
    ordering = ["display_order", "name"]

    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True).anotate(
            # Count related items at the DB level
            active_children_count=Count(
                "children", filter=Q(children__is_active=True), distinct=True
            ),
            active_products_count=Count(
                "products", filter=Q(products__is_active=True), distinct=True
            ).select_related("parent"),
        )

        if self.action == "list":
            is_active = self.request.query_params.get("is_activ")
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active.lower() == "true")

            root_only = self.request.query_params.get("root_only")
            if root_only and root_only.lower() == "true":
                queryset = queryset.filter(parent__isnull=True)

        return queryset

    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        """Get products in this category"""
        category = self.get_object()
        products = Product.objects.filter(
            category=category, is_active=True
        ).prefetch_related(
            Prefetch(
                "images",
                queryset=Product.objects.filter(is_primary=True),
                to_attr="primary_img",
            )
        )

        serializer = ProductListSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data)
