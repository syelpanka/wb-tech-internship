import logging
from decimal import Decimal
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps.cart.models import CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer

logger = logging.getLogger(__name__)


# Create your views here.
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user).select_related('product')

        if not cart_items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка остатков и баланса
        total = Decimal('0.00')
        items_data = []
        for item in cart_items:
            product = item.product
            if item.quantity > product.stock:
                return Response(
                    {'error': f'Not enough stock for {product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item_total = product.price * item.quantity
            total += item_total
            items_data.append({
                'product': product,
                'quantity': item.quantity,
                'price': product.price
            })

        if user.profile.balance < total:
            return Response(
                {'error': 'Insufficient balance'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создание заказа
        order = Order.objects.create(
            user=user,
            total=total
        )

        for data in items_data:
            OrderItem.objects.create(
                order=order,
                product=data['product'],
                quantity=data['quantity'],
                price=data['price']
            )
            # Списание со склада
            data['product'].stock -= data['quantity']
            data['product'].save()

        # Списание баланса
        user.profile.balance -= total
        user.profile.save()

        # Очистка корзины
        cart_items.delete()

        # Логирование
        logger.info(
            f"Order {order.id} created for user {user.username}, total: {total}"
        )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
