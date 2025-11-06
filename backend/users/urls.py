from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import UserProfileViewSet

# router = DefaultRouter()
router = SimpleRouter()
router.register(r"profiles", UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path("", include(router.urls)),
]
