from django.test import TestCase, RequestFactory
from django.http import Http404
from unittest.mock import Mock

from tenants.middleware import TenantAwareMiddleware


class TestTenantAwareMiddleware(TestCase):
    def setUp(self):
        from tenants.models import Tenant

        self.factory = RequestFactory()
        self.tenant = Tenant.objects.create(
            name="Test Middleware", subdomain="testmiddleware", active=True
        )

    def test_middleware_extracts_subdomain_from_host(self):
        middleware = TenantAwareMiddleware(get_response=Mock())

        self.assertEqual(middleware.get_subdomain("testshop.example.com"), "testshop")
        self.assertEqual(middleware.get_subdomain("shop1.mystore.com"), "shop1")

    def test_middleware_handles_no_subdomain(self):
        middleware = TenantAwareMiddleware(get_response=Mock())

        self.assertIsNone(middleware.get_subdomain("example.com"))
        self.assertIsNone(middleware.get_subdomain("localhost"))

    def test_middleware_sets_tenant_context_for_valid_subdomain(self):
        from tenants.context import get_current_tenant

        context_tenant = None

        def mock_get_response(request):
            nonlocal context_tenant
            context_tenant = get_current_tenant()
            return Mock()

        middleware = TenantAwareMiddleware(get_response=mock_get_response)

        request = self.factory.get("/", HTTP_HOST="testmiddleware.example.com")

        _ = middleware(request)

        self.assertEqual(context_tenant, self.tenant)

    def test_middleware_raises_404_for_invalid_subdomain(self):
        middleware = TenantAwareMiddleware(get_response=Mock())

        request = self.factory.get("/", HTTP_HOST="nonexistent.example.com")

        with self.assertRaises(Http404):
            middleware(request)

    def test_middleware_raises_404_for_inactive_tenant(self):
        self.tenant.active = False
        self.tenant.save()

        middleware = TenantAwareMiddleware(get_response=Mock())

        request = self.factory.get("/", HTTP_HOST="testmiddleware.example.com")

        with self.assertRaises(Http404):
            middleware(request)

    def test_middleware_disables_tenant_context_for_admin_path(self):
        from tenants.context import get_state

        context_state = None

        def mock_get_response(request):
            nonlocal context_state
            context_state = get_state()
            return Mock()

        middleware = TenantAwareMiddleware(get_response=mock_get_response)

        request = self.factory.get(
            "/admin/dashboard/", HTTP_HOST="testmiddleware.example.com"
        )

        _ = middleware(request)

        self.assertFalse(context_state["enabled"])
