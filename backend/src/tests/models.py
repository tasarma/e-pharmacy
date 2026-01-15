from django.db import models

from tenants.models import TenantAwareModel


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
