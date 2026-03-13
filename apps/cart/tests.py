from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from apps.products.models import Product
from apps.cart.models import CartItem

class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Тестовый товар',
            price=100.00,
            stock=5
        )
        self.product2 = Product.objects.create(
            name='Товар 2',
            price=200.00,
            stock=3
        )
        self.cart_url = reverse('cart-list')
        self.add_url = reverse('cart-add')
        self.update_url = lambda pid: reverse('cart-update', args=[pid])
        self.remove_url = lambda pid: reverse('cart-remove', args=[pid])

        from rest_framework_simplejwt.tokens import RefreshToken
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_add_to_cart_success(self):
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post(self.add_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        item = CartItem.objects.first()
        self.assertEqual(item.quantity, 2)

    def test_add_existing_product_updates_quantity(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=1)
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post(self.add_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = CartItem.objects.get(user=self.user, product=self.product)
        self.assertEqual(item.quantity, 3)

    def test_add_to_cart_exceeds_stock(self):
        data = {'product_id': self.product.id, 'quantity': 10}
        response = self.client.post(self.add_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_add_invalid_product(self):
        data = {'product_id': 999, 'quantity': 1}
        response = self.client.post(self.add_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cart_list(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        CartItem.objects.create(user=self.user, product=self.product2, quantity=1)
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 2)
        self.assertEqual(response.data['total'], 2*100 + 1*200)

    def test_update_quantity_success(self):
        item = CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        data = {'quantity': 3}
        response = self.client.patch(self.update_url(self.product.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

    def test_update_quantity_exceeds_stock(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        data = {'quantity': 10}
        response = self.client.patch(self.update_url(self.product.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_from_cart(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=1)
        response = self.client.delete(self.remove_url(self.product.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_remove_nonexistent_item(self):
        response = self.client.delete(self.remove_url(self.product.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        self.client.credentials()
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
