from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from apps.products.models import Product


class ProductTests(APITestCase):
    """Тесты для товаров"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        self.product = Product.objects.create(
            name='Тестовый товар',
            description='Описание',
            price=100.00,
            stock=5
        )
        self.list_url = reverse('product-list')
        self.detail_url = reverse('product-detail', args=[self.product.pk])

    def get_token_for_user(self, user):
        """Получение JWT токена для пользователя"""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_product_list_unauthenticated(self):
        """Неавторизованный пользователь может получить список товаров"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.product.name)

    def test_product_list_authenticated(self):
        """Авторизованный пользователь может получить список товаров"""
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_detail_unauthenticated(self):
        """Неавторизованный пользователь может получить детали товара"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)

    def test_create_product_as_admin(self):
        """Админ может создать товар"""
        token = self.get_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {
            'name': 'Новый товар',
            'description': 'Новое описание',
            'price': 200.00,
            'stock': 10
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.last().name, 'Новый товар')

    def test_create_product_as_regular_user(self):
        """Обычный пользователь не может создать товар"""
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'name': 'Новый товар', 'price': 200.00, 'stock': 10}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)

    def test_create_product_unauthenticated(self):
        """Неавторизованный пользователь не может создать товар"""
        data = {'name': 'Новый товар', 'price': 200.00, 'stock': 10}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Product.objects.count(), 1)

    def test_update_product_as_admin(self):
        """Админ может обновить товар"""
        token = self.get_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'name': 'Обновлённый товар', 'price': 150.00}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Обновлённый товар')
        self.assertEqual(self.product.price, 150.00)

    def test_update_product_as_regular_user(self):
        """Обычный пользователь не может обновить товар"""
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'name': 'Хакнутый товар'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Тестовый товар')

    def test_delete_product_as_admin(self):
        """Админ может удалить товар"""
        token = self.get_token_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_product_as_regular_user(self):
        """Обычный пользователь не может удалить товар"""
        token = self.get_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)

    def test_delete_product_unauthenticated(self):
        """Неавторизованный пользователь не может удалить товар"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Product.objects.count(), 1)

    def test_get_nonexistent_product(self):
        """Запрос несуществующего товара возвращает 404"""
        url = reverse('product-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)