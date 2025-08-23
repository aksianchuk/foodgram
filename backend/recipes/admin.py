from django.contrib import admin

from recipes.models import (
    Ingredient, 
    Recipe, 
    RecipeIngredient, 
    Subscription, 
    Tag
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = [
        'id',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'get_ingredients'
    ]

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join(
            f'{item.ingredient.name} - {item.amount} '
            f'({item.ingredient.measurement_unit})'
            for item in obj.recipe_ingredients.all()
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'subscribing']
