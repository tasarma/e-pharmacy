"""
Add follwing to /etc/hosts file to run it successfully:
    127.0.0.1    tenant1.example.com
    127.0.0.1    tenant2.example.com
"""

from django.test import TestCase, Client, RequestFactory
from django.http import Http404, HttpResponse
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import models
from unittest.mock import patch
import uuid

from tenants.models import Tenant, TenantAwareModel
from tenants.middleware import TenantAwareMiddleware
from tenants.context import set_tenant_context, tenant_context_disabled
from tenants.middleware import TenantAwareMiddleware

from tests.models import TestProduct


class TestTenantIntegration(TestCase):
    """
    Integration tests for multi-tenant functionality
    """
    def setUp(self):
        self.client = Client()

        self.tenant1 = Tenant.objects.create(
            name="Tenant One",
            subdomain="tenant1",
            active=True
        )
        self.tenant2 = Tenant.objects.create(
            name="Tenant Two", 
            subdomain="tenant2",
            active=True
        )
        
        # Create test users
        User = get_user_model()
        self.user1 = User.objects.create_user(
            email="user1@tenant1.com",
            password="testpass123",
            tenant=self.tenant1
        )
        self.user2 = User.objects.create_user(
            email="user2@tenant2.com", 
            password="testpass123",
            tenant=self.tenant2
        )
        
        # Create test data for each tenant
        with set_tenant_context(tenant=self.tenant1):
            self.product1_tenant1 = TestProduct.objects.create(
                name="Product 1 - Tenant 1",
                price=10.00
            )
            self.product2_tenant1 = TestProduct.objects.create(
                name="Product 2 - Tenant 1", 
                price=20.00
            )
        
        with set_tenant_context(tenant=self.tenant2):
            self.product1_tenant2 = TestProduct.objects.create(
                name="Product 1 - Tenant 2",
                price=15.00
            )

    def test_tenant_isolation_via_http_requests(self):
        with set_tenant_context(self.tenant1):
            response = self.client.get(
                "/api/products/",
                HTTP_HOST="tenant1.example.com"
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 2)
            self.assertTrue(all("Tenant 1" in p["name"] for p in data))

        with set_tenant_context(self.tenant2):
            response = self.client.get(
                "/api/products/",
                HTTP_HOST="tenant2.example.com"
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 1)
            self.assertTrue("Tenant 2" in data[0]["name"])

    def test_unknown_tenant_returns_404(self):
        # Create a request for a tenant that does NOT exist
        factory = RequestFactory()
        request = factory.get("/api/products/", HTTP_HOST="tenant3.example.com")

        # Middleware wrapping a dummy view that would normally access tenant-aware models
        def dummy_view(req):
            # If this runs, tenant context would normally be required
            return HttpResponse("OK")

        middleware = TenantAwareMiddleware(dummy_view)

        # Assert that accessing the middleware with an unknown tenant raises Http404
        with self.assertRaises(Http404) as cm:
            middleware(request)

    def test_user_access_is_limited_to_their_tenant(self):
        User = get_user_model()

        with set_tenant_context(self.tenant1):
            self.client.login(email="user1@tenant1.com", password="testpass123")
            response = self.client.get("/api/products/", HTTP_HOST="tenant1.example.com")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(all("Tenant 1" in p["name"] for p in data))
            self.assertEqual(len(data), 2)

        with set_tenant_context(self.tenant2):
            self.client.login(email="user2@tenant2.com", password="testpass123")
            response = self.client.get("/api/products/", HTTP_HOST="tenant2.example.com")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(all("Tenant 2" in p["name"] for p in data))
            self.assertEqual(len(data), 1)

        with set_tenant_context(self.tenant2):
            self.client.login(email="user1@tenant1.com", password="testpass123")
            response = self.client.get("/api/products/", HTTP_HOST="tenant2.example.com")
            self.assertEqual(response.status_code, 404)

