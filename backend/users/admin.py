from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    """Админка пользователя."""

    list_display = ('id', 'username', 'email', 'password')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'
    list_filter = ('username', 'email')


admin.site.register(User, CustomUserAdmin)
