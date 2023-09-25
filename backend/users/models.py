from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        verbose_name='Логин',
    )
    email = models.EmailField(
        db_index=True,
        unique=True,
        max_length=254,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )
    is_subcribed = models.BooleanField(
        default=False,
        verbose_name='Подписка на данного автора',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
        return self.username
