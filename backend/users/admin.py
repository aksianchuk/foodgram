from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Админ-панель для пользователя.

    - Отображает имя пользователя, имя, фамилию и электронную почту,
    - Позволяет фильтровать пользователей по имени пользователя и электронной
      почте.
    """

    list_display = ['username', 'first_name', 'last_name', 'email']
    search_fields = ['username', 'email']
