from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.constants import (
    MAX_EMAIL,
    MAX_FIRST_NAME,
    MAX_LAST_NAME,
    MAX_USERNAME,
)


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Хранит адрес электронной почты, имя пользователя, имя, фамилию и аватар.
    """

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=MAX_EMAIL,
        unique=True,
        blank=False
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_USERNAME,
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_FIRST_NAME,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LAST_NAME,
        blank=False
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

    def __str__(self):
        return self.email
