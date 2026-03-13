from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import CartItem
from apps.products.models import Product
from .serializers import (
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)


# Create your views here.
class CartListView(APIView):
    """Просмотр корзины: GET /api/cart/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(items, many=True)
        total = sum(item.product.price * item.quantity for item in items)
        return Response({
            'items': serializer.data,
            'total': total
        })


class AddToCartView(APIView):
    """Добавить товар в корзину: POST /api/cart/add/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            product = get_object_or_404(Product, pk=product_id)

            if quantity > product.stock:
                return Response(
                    {'error': 'Not enough stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    return Response(
                        {'error': 'Not enough stock'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.quantity = new_quantity
                cart_item.save()

            return Response(
                CartItemSerializer(cart_item).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UpdateCartItemView(APIView):
    """
    Изменить количество товара в корзине:
    PATCH /api/cart/update/<product_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        cart_item = get_object_or_404(
            CartItem,
            user=request.user,
            product=product
        )

        serializer = UpdateCartItemSerializer(data=request.data)
        if serializer.is_valid():
            new_quantity = serializer.validated_data['quantity']
            if new_quantity > product.stock:
                return Response(
                    {'error': 'Not enough stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()
            return Response(CartItemSerializer(cart_item).data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class RemoveFromCartView(APIView):
    """
    Удалить товар из корзины:
    DELETE /api/cart/remove/<product_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        cart_item = get_object_or_404(
            CartItem,
            user=request.user,
            product=product
        )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
