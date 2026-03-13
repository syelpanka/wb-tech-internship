from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class UserRegistrationTests(APITestCase):
    """Тесты регистрации пользователя"""

    def test_registration_success(self):
        """Успешная регистрация нового пользователя"""
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'StrongPass123',
            'email': 'test@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertNotIn('password', response.data)

        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(float(user.profile.balance), 0.00)

    def test_registration_duplicate_username(self):
        """Попытка регистрации с уже существующим username"""
        User.objects.create_user(username='testuser', password='pass123')
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'anotherpass',
            'email': 'another@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_missing_fields(self):
        """Регистрация без обязательных полей"""
        url = reverse('register')
        data = {'username': 'incomplete'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('email', response.data)


class UserLoginTests(APITestCase):
    """Тесты получения JWT токенов"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_login_success(self):
        """Успешный вход с правильными учетными данными"""
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        """Вход с неправильным паролем"""
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Вход с несуществующим пользователем"""
        url = reverse('token_obtain_pair')
        data = {'username': 'ghost', 'password': 'pass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTests(APITestCase):
    """Тесты получения профиля"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_profile_authenticated(self):
        """Доступ к профилю с валидным токеном"""
        url = reverse('profile')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertIn('balance', response.data)

    def test_profile_unauthenticated(self):
        """Доступ к профилю без токена"""
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_invalid_token(self):
        """Доступ с невалидным токеном"""
        url = reverse('profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid.token.here')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DepositTests(APITestCase):
    """Тесты пополнения баланса"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

    def test_deposit_success(self):
        """Успешное пополнение баланса"""
        url = reverse('deposit')
        data = {'amount': 100.50}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['balance']), 100.50)
        self.user.profile.refresh_from_db()
        self.assertEqual(float(self.user.profile.balance), 100.50)

    def test_deposit_negative_amount(self):
        """Пополнение на отрицательную сумму"""
        url = reverse('deposit')
        data = {'amount': -50}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deposit_zero_amount(self):
        """Пополнение на ноль"""
        url = reverse('deposit')
        data = {'amount': 0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deposit_non_numeric(self):
        """Пополнение с некорректным значением"""
        url = reverse('deposit')
        data = {'amount': 'abc'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deposit_missing_amount(self):
        """Запрос без поля amount"""
        url = reverse('deposit')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deposit_unauthenticated(self):
        """Пополнение без токена"""
        self.client.credentials()
        url = reverse('deposit')
        data = {'amount': 100}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
