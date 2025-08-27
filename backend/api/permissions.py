from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    """
    Разрешение только для безопасных методов (GET, HEAD, OPTIONS).

    Используется для предоставления только чтения без возможности изменения
    объекта.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAuthor(BasePermission):
    """
    Разрешение, которое позволяет редактировать объект только его автору.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
