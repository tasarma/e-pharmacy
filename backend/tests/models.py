from django.test import TestCase, TransactionTestCase
from users.models import CustomUser as User
from django.db import models, connection
from unittest.mock import patch

from tenants.models import Tenant, TenantAwareModel


class TestOrder(TenantAwareModel):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"


class TestProduct(TenantAwareModel):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        app_label = "tests"
        managed = True
