from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=60, unique=True, db_index=True)
