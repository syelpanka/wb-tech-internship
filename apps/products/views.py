from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET: список всех товаров (всем)
    POST: создание нового товара (админ)
    """
    authentication_classes = [JWTAuthentication]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


@method_decorator(csrf_exempt, name='dispatch')
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: детальная информация о товаре (всем)
    PUT/PATCH: обновление товара (админ)
    DELETE: удаление товара (админ)
    """
    authentication_classes = [JWTAuthentication]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
