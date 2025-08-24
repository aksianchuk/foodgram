from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from users.constants import (
    MAX_EMAIL,
    MAX_FIRST_NAME,
    MAX_LAST_NAME,
    MAX_USERNAME,
)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

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
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Имя пользователя может содержать только латинские буквы '
                    'цифры и символы _ . @ + -'
                )
            )
        ]
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
