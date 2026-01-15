from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ProductImageViewSet,
    ProductTagViewSet,
)


router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"images", ProductImageViewSet, basename="product-image")
router.register(r"tags", ProductTagViewSet, basename="product-tag")

urlpatterns = [
    path("", include(router.urls)),
]
