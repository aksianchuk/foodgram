from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (
    MAX_INGREDIENT_NAME,
    MAX_MEASUREMENT_UNIT,
    MAX_RECIPE_NAME,
    MAX_TAG_NAME,
    MAX_TAG_SLUG,
)


User = get_user_model()


class UserRecipeBase(models.Model):
    """
    Абстрактная модель для связи пользователя с рецептом.

    Хранит пользователя и рецепт.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s_user_recipe',
                violation_error_message=(
                    'Этот рецепт уже добавлен.'
                )
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Tag(models.Model):
    """
    Модель тега для рецептов.

    Хранит название тега и slug для использования в URL.
    """

    name = models.CharField(
        'Название',
        max_length=MAX_TAG_NAME,
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        'Slug',
        max_length=MAX_TAG_SLUG,
        unique=True,
        blank=False
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингредиента для рецептов.

    Хранит название ингредиента и единицы измерения.
    """

    name = models.CharField(
        'Название',
        max_length=MAX_INGREDIENT_NAME,
        unique=True,
        blank=False
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=MAX_MEASUREMENT_UNIT,
        blank=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit',
                violation_error_message=(
                    'Ингредиент с таким названием и единицей измерения уже '
                    'существует.'
                )
            )
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """
    Модель рецепта.

    Хранит автора, название, фотографию, описание, ингредиенты, теги, время
    приготовления и дату добавления.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=MAX_RECIPE_NAME)
    image = models.ImageField(
        'Фотография',
        upload_to='recipes/images/',
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField('Добавлен', auto_now_add=True)

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Модель для связи рецептов с ингредиентами и их количеством.

    Хранит рецепт, ингредиент и количество ингредиента.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        ordering = ['recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
                violation_error_message=(
                    'Этот ингредиент уже добавлен к рецепту.'
                )
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class Subscription(models.Model):
    """
    Модель подписок.

    Хранит пользователя и пользователя на которого он подписан.
    """

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscriptions'
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписка',
        related_name='subscribers'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['subscriber']
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribing'],
                name='unique_subscriber_subscribing',
                violation_error_message=(
                    'Вы уже подписаны на этого пользователя.'
                )
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('subscribing')),
                name='check_not_self_subscribe'
            )
        ]

    def __str__(self):
        return f'{self.subscriber} {self.subscribing}'


class Favorite(UserRecipeBase):
    """
    Модель избранного.
    """

    class Meta(UserRecipeBase.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(UserRecipeBase):
    """
    Модель списка покупок.
    """

    class Meta(UserRecipeBase.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
