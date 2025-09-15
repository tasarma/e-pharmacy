from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import TenantAwareTokenObtainSerializer


class TenantAwareTokenObtainView(TokenObtainPairView):
    serializer_class = TenantAwareTokenObtainSerializer
