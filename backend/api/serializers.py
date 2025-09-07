from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.utils import Base64ImageField
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


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователя."""

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name']


class UserRegisterSerializer(BaseUserSerializer):
    """Сериализатор для регистрации пользователя с паролем."""

    password = serializers.CharField(write_only=True, required=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(BaseUserSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['is_subscribed', 'avatar']

    def get_is_subscribed(self, obj):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and request.user.subscriptions.filter(subscribing=obj).exists()
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar']


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов рецепта."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """"Сериализатор для ингредиентов рецепта."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """"Сериализатор для чтения ингредиентов рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """"Сериализатор для записи ингредиентов рецепта."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

    def validate_amount(self, value):
        if value < 0.1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше нуля.'
            )
        return value


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        """
        Проверяет, добавил ли пользователь рецепт в избранное.

        Возвращает:
            bool: True, если рецепт в избранном, иначе False.
        """
        request = self.context['request']
        return (
            request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, добавил ли пользователь рецепт в список покупок.

        Возвращает:
            bool: True, если рецепт в списке попкупок, иначе False.
        """
        request = self.context['request']
        return (
            request.user.is_authenticated
            and request.user.shopping_cart.filter(recipe=obj).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецепта."""

    ingredients = RecipeIngredientWriteSerializer(
        source='recipe_ingredients',
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def validate(self, data):
        if 'recipe_ingredients' not in data or not data['recipe_ingredients']:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один ингредиент.'
            )
        if 'tags' not in data or not data['tags']:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один тег.'
            )
        ingredients_ids = [item['id'] for item in data['recipe_ingredients']]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        tags_ids = data['tags']
        if len(tags_ids) != len(set(tags_ids)):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self._create_recipe_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.recipe_ingredients.all().delete()
        self._create_recipe_ingredients(instance, ingredients)
        instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    @staticmethod
    def _create_recipe_ingredients(recipe, ingredients):
        """Создает объекты RecipeIngredient и сохраняет их через bulk_create.

        Параметры:
        - recipe: рецепт, к которому будут привязаны ингредиенты
        - ingredients: список словарей, каждый с ключами:
            - 'id': идентификатор ингредиента
            - 'amount': количество ингредиента
        """
        ingredient_objects = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredient_objects)


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенного рецепта."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class SubscribedUserWithRecipesSerializer(UserSerializer):
    """Сериализатор для пользователя на которого подписка."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        ]

    def get_recipes(self, obj):
        """
        Возвращает список рецептов.

        Если в query-параметрах передан recipes_limit и он является числом,
        возвращается только указанное количество рецептов.

        Возвращает:
            list: Список рецептов, сериализованных с помощью
            RecipeShortSerializer.
        """
        request = self.context.get('request')
        recipes_limit = (
            request.query_params.get('recipes_limit') if request else None
        )
        recipes_queryset = obj.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            recipes_queryset = recipes_queryset[:int(recipes_limit)]
        return RecipeShortSerializer(recipes_queryset, many=True).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на пользователя."""

    subscribing = (
        serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    )

    class Meta:
        model = Subscription
        fields = ['subscribing']

    def validate(self, data):
        subscriber = self.context['request'].user
        subscribing = data['subscribing']

        if subscriber == subscribing:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Subscription.objects.filter(
            subscriber=subscriber, subscribing=subscribing
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        return data

    def save(self):
        subscription = Subscription.objects.create(
            subscriber=self.context['request'].user,
            subscribing=self.validated_data['subscribing']
        )
        return subscription


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def validate(self, attrs):
        user_id = attrs.get('user')
        recipe_id = attrs.get('recipe')

        if Favorite.objects.filter(
            user=user_id,
            recipe=recipe_id
        ).exists():
            raise serializers.ValidationError('Рецепт уже добавлен.')
        return attrs

    def to_representation(self, instance):
        return RecipeShortSerializer(instance, context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в список покупок."""

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']

    def validate(self, attrs):
        user_id = attrs.get('user')
        recipe_id = attrs.get('recipe')

        if ShoppingCart.objects.filter(
            user=user_id,
            recipe=recipe_id
        ).exists():
            raise serializers.ValidationError('Рецепт уже добавлен.')
        return attrs

    def to_representation(self, instance):
        return RecipeShortSerializer(instance, context=self.context).data
