from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Все пользователи могут просматривать товары,
    только админ может создавать/редактировать/удалять.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
