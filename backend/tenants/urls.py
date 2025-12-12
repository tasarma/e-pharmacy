from django.urls import path
from .views import TenantOnboardingView, TenantSettingsView


urlpatterns = [
    path("register/", TenantOnboardingView.as_view(), name="tenant-register"),
    path("settings/", TenantSettingsView.as_view(), name="tenant-settings"),
]
