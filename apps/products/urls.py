from django.urls import path
from .views import ProductListCreateView, ProductDetailView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path(
        '',
        csrf_exempt(ProductListCreateView.as_view()),
        name='product-list',
    ),
    path(
        '<int:pk>/',
        csrf_exempt(ProductDetailView.as_view()),
        name='product-detail',
    ),
]