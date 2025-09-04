from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Админ-панель для тегов рецептов.

    - Отображает название тега и slug для использования в URL.
    """

    list_display = ['name', 'slug']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-панель для ингредиентов рецептов.

    - Отображает название ингредиента и единицы измерения.
    """

    list_display = ['name', 'measurement_unit']
    search_fields = ['name']


class RecipeIngredientInline(admin.TabularInline):
    """
    Встраиваемая таблица для ингредиентов рецепта.

    - Позволяет редактировать ингредиенты прямо на странице рецепта.
    """

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-панель рецепта.

    - Отображает название имя и автора рецепта в списке,
    - Позволяет фильтровать рецепты по тегам,
    - Позволяет редактировать ингредиенты на странице рецепта,
    - Позволяет увидеть количество добавлений рецепта в избранноое на странице
      рецепта.
    """

    list_display = ['name', 'author']
    list_filter = ['tags']
    readonly_fields = ['favorites_count']
    inlines = [RecipeIngredientInline]

    @admin.display(description='Добавлено в избранное')
    def favorites_count(self, obj):
        return obj.favorited_by.count()

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join(
            f'{item.ingredient.name} - {item.amount} '
            f'({item.ingredient.measurement_unit})'
            for item in obj.recipe_ingredients.all()
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Админ-панель для подписок.

    - Отображает пользователя и пользователя на которого он подписан.
    """

    list_display = ['subscriber', 'subscribing']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Админ-панель для избранного.

    - Отображает пользователя и рецепт, который он добавил в избранное.
    """

    list_display = ['user', 'recipe']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Админ-панель для избранного.

    - Отображает пользователя и рецепт, который он добавил в список покупок.
    """

    list_display = ['user', 'recipe']
