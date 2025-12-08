from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantOnboardingView, TenantSettingsViewSet

router = DefaultRouter()
router.register(r'settings', TenantSettingsViewSet, basename='tenant-settings')

urlpatterns = [
    path('register/', TenantOnboardingView.as_view(), name='tenant-register'),
    path('', include(router.urls)),
]
