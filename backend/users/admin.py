from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Админ-панель для пользователя.

    - Отображает имя пользователя, имя, фамилию и электронную почту,
    - Позволяет фильтровать пользователей по имени пользователя и электронной
      почте.
    """

    list_display = ['username', 'first_name', 'last_name', 'email']
    search_fields = ['username', 'email']
