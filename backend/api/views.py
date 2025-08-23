from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.permissions import IsAuthor, ReadOnly
from api.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    TagSerializer,
    UserAvatarSerializer,
    UserRegisterSerializer,
    UserSerializer
)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()

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
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data['new_password']
        )
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['put', 'delete'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def manage_avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(
                user,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=True)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [ReadOnly()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        if self.action == 'manage_avatar':
            return UserAvatarSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return UserSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [ReadOnly]
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [ReadOnly]
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        return self._add_or_remove_recipe(
            request=request,
            model=Favorite,
            recipe=recipe,
            user=request.user,
        )

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        return self._add_or_remove_recipe(
            request=request,
            model=ShoppingCart,
            recipe=recipe,
            user=request.user,
        )

    def _add_or_remove_recipe(self, request, model, recipe, user):
        exists = model.objects.filter(user=user, recipe=recipe).exists()
        if request.method == 'POST':
            if exists:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipe=recipe)
            return Response(
                self.get_serializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not exists:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'update':
            return [ReadOnly()]
        if self.action in ['partial_update', 'destroy']:
            return [IsAuthor()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer
        if self.action in ['favorite', 'shopping_cart']:
            return RecipeShortSerializer
        return RecipeReadSerializer
