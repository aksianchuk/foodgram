from django.contrib.auth import get_user_model
from django.db.models import Count, F, Prefetch, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import int_to_base36
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthor, ReadOnly
from api.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    SubscribedUserWithRecipesSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserAvatarSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)


User = get_user_model()


class UserViewSet(ModelViewSet):
    """ViewSet для пользователя."""

    queryset = User.objects.all()

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Возвращает данные текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False
    )
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
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
        url_path='me/avatar'
    )
    def manage_avatar(self, request):
        """Изменение аватара текущего пользователя."""
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
        if user.avatar:
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Подписки текущего пользователя."""
        subscribed_users = User.objects.filter(
            subscribers__subscriber=request.user
        ).prefetch_related(
            # Получаем только конкретные значения, чтобы не нагружать БД.
            Prefetch(
                'recipes',
                queryset=Recipe.objects.only(
                    'id', 'name', 'image', 'cooking_time'
                )
            )
        ).annotate(recipes_count=Count('recipes')).order_by('id')
        serializer = SubscribedUserWithRecipesSerializer(
            self.paginate_queryset(subscribed_users),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post']
    )
    def subscribe(self, request, pk=None):
        """Подписка на пользователя/Отписка от пользователя."""
        subscribing_user = self._get_subscribing_user(pk)
        serializer = SubscribeSerializer(
            data={'subscribing': subscribing_user.pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_serializer = SubscribedUserWithRecipesSerializer(
            subscribing_user,
            context={'request': request}
        )
        return Response(
            user_serializer.data, status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        subscribing_user = self._get_subscribing_user(pk)
        deleted_subscription_count, _ = Subscription.objects.filter(
            subscriber=request.user,
            subscribing=subscribing_user
        ).delete()
        if deleted_subscription_count:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def _get_subscribing_user(self, pk):
        """
        Возвращает пользователя для подписки(отписки) с аннотацией количества
        рецептов.
        """
        return get_object_or_404(
            User.objects.annotate(recipes_count=Count('recipes')),
            pk=pk
        )

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        if self.action == 'manage_avatar':
            return UserAvatarSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return UserSerializer


class TagViewSet(ReadOnlyModelViewSet):
    """ViewSet для тегов рецепта."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet для ингредиентов рецепта."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """ViewSet для рецепта."""

    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    @action(
        methods=['post', 'delete'],
        detail=True
    )
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное пользователя."""
        recipe = self.get_object()
        return self._add_or_remove_recipe(
            request=request,
            model=Favorite,
            recipe=recipe,
            user=request.user
        )

    @action(
        methods=['post', 'delete'],
        detail=True
    )
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в список покупок пользователя."""
        recipe = self.get_object()
        return self._add_or_remove_recipe(
            request=request,
            model=ShoppingCart,
            recipe=recipe,
            user=request.user
        )

    @action(
        methods=['get'],
        detail=True,
        url_path='get-link'
    )
    def short_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        return Response(
            {
                'short-link':
                f'{request.scheme}://{request.get_host()}/s/'
                f'{int_to_base36(int(pk))}'
            },
            status=status.HTTP_200_OK
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Получение списка покупок."""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values(
                name=F('ingredient__name'),
                measurement_unit=F('ingredient__measurement_unit')
            )
            .annotate(amount=Sum('amount'))
            .order_by('name')
        )
        if not ingredients.exists():
            return Response(
                {
                    'detail': 'Список покупок пуст.'
                },
                status=status.HTTP_204_NO_CONTENT
            )
        lines = [
            f'{i}. {ingredient["name"]} - {ingredient["amount"]} '
            f'({ingredient["measurement_unit"]})'
            for i, ingredient in enumerate(ingredients, start=1)
        ]
        return HttpResponse(
            content='\n'.join(lines),
            content_type='text/plain; charset=utf-8',
            headers={
                'Content-Disposition':
                'attachment; filename="shopping_cart.txt"'
            }
        )

    def _add_or_remove_recipe(self, request, model, recipe, user):
        """Добавляет или удаляет рецепт для пользователя в указанной модели."""
        exists = model.objects.filter(user=user, recipe=recipe).exists()
        if request.method == 'POST':
            if exists:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipe=recipe)
            return Response(
                self.get_serializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
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
