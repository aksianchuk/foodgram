from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.permissions import ReadOnly
from api.serializers import AvatarSerializer, UserSerializer


User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        serializer_class=SetPasswordSerializer,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('put', 'delete'),
        detail=False,
        serializer_class=AvatarSerializer,
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(instance=user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = self.get_serializer(
                user,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'update':
            return [ReadOnly()]
        if self.action == 'partial_update':
            return [ReadOnly()]
        if self.action == 'destroy':
            return [ReadOnly()]
        return super().get_permissions()
