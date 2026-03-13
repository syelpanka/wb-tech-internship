from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from apps.products.models import Product
from apps.cart.models import CartItem
from apps.orders.models import Order


class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user.profile.balance = 1000
        self.user.profile.save()

        self.product1 = Product.objects.create(
            name='Товар 1',
            price=100.00,
            stock=5
        )
        self.product2 = Product.objects.create(
            name='Товар 2',
            price=200.00,
            stock=3
        )
        self.create_order_url = reverse('order-create')

        from rest_framework_simplejwt.tokens import RefreshToken
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_order_success(self):
        CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=2
        )
        CartItem.objects.create(
            user=self.user,
            product=self.product2,
            quantity=1
        )

        response = self.client.post(self.create_order_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.total, 2*100 + 1*200)
        self.assertEqual(order.items.count(), 2)

        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, 3)
        self.assertEqual(self.product2.stock, 2)

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.balance, 1000 - (2*100 + 1*200))

        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)

    def test_create_order_empty_cart(self):
        response = self.client.post(self.create_order_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_insufficient_stock(self):
        CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=10
        )
        response = self.client.post(self.create_order_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_insufficient_balance(self):
        self.user.profile.balance = 50
        self.user.profile.save()
        CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=1
        )
        response = self.client.post(self.create_order_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
