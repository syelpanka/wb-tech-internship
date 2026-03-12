from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer
from decimal import Decimal, InvalidOperation


# Create your views here.
class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    Доступ для всех пользователей.
    POST /api/auth/register/
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(APIView):
    """
    Просмотр профиля.
    Требуется аутентификация текущего пользовалтеля.
    GET /api/auth/profile/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Возвращает профиль текущего пользователя.
        """

        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


class DepositView(APIView):
    """
    Пополнение баланса текущего пользователя.
    Требуется аутентификация текущего пользовалтеля.
    POST /api/auth/deposit/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        if amount is None:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                raise ValueError
        except (ValueError, InvalidOperation, TypeError):
            return Response(
                {'error': 'Amount must be a positive number'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = request.user.profile

        profile.balance += amount
        profile.save()

        return Response(
            {'balance': str(profile.balance)},
            status=status.HTTP_200_OK
        )
