from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Админ-панель для пользователя.

    - Отображает имя пользователя, имя, фамилию, электронную почту, количество
    подписчиков и количество рецептов.
    - Позволяет фильтровать пользователей по имени пользователя и электронной
      почте.
    """

    list_display = [
        'username',
        'first_name',
        'last_name',
        'email',
        'subscribers_count',
        'recipes_count'
    ]
    search_fields = ['username', 'email']

    @admin.display(description='Количество подписчиков')
    def subscribers_count(self, obj):
        return obj.subscribers.count()

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()
