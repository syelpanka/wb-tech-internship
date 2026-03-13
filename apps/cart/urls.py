from django.urls import path
from .views import (
    CartListView,
    AddToCartView,
    UpdateCartItemView,
    RemoveFromCartView
)

urlpatterns = [
    path('', CartListView.as_view(), name='cart-list'),
    path('add/', AddToCartView.as_view(), name='cart-add'),
    path('update/<int:product_id>/', UpdateCartItemView.as_view(), name='cart-update'),
    path('remove/<int:product_id>/', RemoveFromCartView.as_view(), name='cart-remove'),
]
