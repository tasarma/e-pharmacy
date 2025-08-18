from django.urls import path
from .views import test_products_list

urlpatterns = [
    path("api/products/", test_products_list, name="test_products_list"),
]

