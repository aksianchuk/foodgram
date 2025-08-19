from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


MAX_EMAIL_LENGTH = 254
MAX_USERNAME_LENGTH = 150
MAX_FIRST_NAME_LENGTH = 150
MAX_LAST_NAME_LENGTH = 150


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        blank=False
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_FIRST_NAME_LENGTH,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LAST_NAME_LENGTH,
        blank=False
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        null=True,
        default=None
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

    def __str__(self):
        return self.email
