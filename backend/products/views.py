from django.db.models import Count, Q, Prefetch, F
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import structlog

from .models import Category, Product, ProductTag, ProductImage
from .filters import ProductFilter
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductTagSerializer,
    StockAdjustmentSerializer,
)
from .permissions import IsStaffOrReadOnly

from tenants.context import get_current_tenant


logger = structlog.get_logger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for product categories.
    Manager and Super Admin can create/update, all authenticated users can read.
    """

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "display_order", "created_at"]
    ordering = ["display_order", "name"]

    def get_queryset(self):
        queryset = (
            Category.objects.filter(is_active=True)
            .annotate(
                # Count related items at the DB level
                active_children_count=Count(
                    "children", filter=Q(children__is_active=True), distinct=True
                ),
                active_products_count=Count(
                    "products", filter=Q(products__is_active=True), distinct=True
                ),
            )
            .select_related("parent")
        )

        if self.action == "list":
            is_active = self.request.query_params.get("is_active")
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
                queryset=ProductImage.objects.filter(is_primary=True),
                to_attr="primary_img",
            )
        )

        serializer = ProductListSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for products.
    Staff can create/update, all authenticated users can read.
    """

    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ["name", "sku", "barcode", "description"]
    ordering_fields = ["name", "price", "created_at", "stock_quantity"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["list", "low_stock", "out_of_stock", "featured"]:
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        # Primary Image only for 'list' to save memory
        primary_img_prefetch = Prefetch(
            "images",
            queryset=ProductImage.objects.filter(is_primary=True),
            to_attr="primary_img",
        )

        queryset = Product.objects.select_related("category")

        # Detailed prefetch for single object or specific actions
        if self.action in ["retrieve", "update", "partial_update"]:
            return queryset.prefetch_related("images", "tag_assignments__tag")

        # Lightweight prefetch for list views
        return queryset.prefetch_related(primary_img_prefetch)

    def perform_create(self, serializer):
        """Log product creation."""
        product = serializer.save()
        logger.info(
            "product_created",
            product_id=str(product.id),
            sku=product.sku,
            tenant_id=str(get_current_tenant().id),
        )

    def perform_update(self, serializer):
        """Track stock changes on update."""
        instance = self.get_object()
        old_stock = instance.stock_quantity if instance.track_inventory else None

        product = serializer.save()

        if old_stock is not None and product.stock_quantity != old_stock:
            logger.info(
                "product_stock_updated",
                product_id=str(product.id),
                old_stock=old_stock,
                new_stock=product.stock_quantity,
            )

    @action(detail=True, methods=["post"])
    def adjust_stock(self, request, pk=None):
        product = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            product.adjust_stock(
                quantity=serializer.validated_data["quantity"],
                reason=serializer.validated_data["reason"],
                user=request.user,
            )
            return Response(
                {
                    "message": "Stock adjusted successfully",
                    "new_stock": product.stock_quantity,
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        products = self.get_queryset().filter(
            track_inventory=True,
            stock_quantity__lte=F("low_stock_threshold"),
            stock_quantity__gt=0,
        )
        page = self.paginate_queryset(products)
        serializer = self.get_serializer(page or products, many=True)
        return (
            self.get_paginated_response(serializer.data)
            if page
            else Response(serializer.data)
        )

    @action(detail=False, methods=["get"])
    def out_of_stock(self, request):
        """Get out of stock products."""
        products = self.get_queryset().filter(track_inventory=True, stock_quantity=0)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Get featured products."""
        products = self.get_queryset().filter(is_featured=True, is_active=True)[:12]

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ProductImageViewSet(viewsets.ModelViewSet):
    """Manage product images."""

    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return ProductImage.objects.select_related("product")

    def perform_create(self, serializer):
        """Ensure tenant is set."""
        product = serializer.validated_data["product"]
        serializer.save(tenant=product.tenant)


class ProductTagViewSet(viewsets.ModelViewSet):
    """Manage product tags."""

    serializer_class = ProductTagSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering = ["name"]

    def get_queryset(self):
        return ProductTag.objects.all()
