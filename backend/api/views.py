from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import UserSerializer


class CustomUserViewSet(UserViewSet):
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        return super().me(request)

    def activation(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def resend_activation(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_password(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_password_confirm(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_username(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_username_confirm(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)
