from django.http import JsonResponse, Http404
from .models import TestProduct
from tenants.context import get_current_tenant


def test_products_list(request):
    current_user = request.user
    current_tenant = get_current_tenant()

    # Enforce that user belongs to this tenant
    if current_user.is_authenticated and current_user.tenant != current_tenant:
        raise Http404("User cannot access this tenant's data")

    products = TestProduct.objects.all()
    data = [{"id": p.id, "name": p.name, "price": float(p.price)} for p in products]
    return JsonResponse(data, safe=False)
