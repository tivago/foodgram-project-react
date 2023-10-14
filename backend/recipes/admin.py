from django.contrib import admin

from users.models import (Subscription, )
from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)


class IngredientInRecipeInline(admin.TabularInline):
    """Админка ингредиентов в рецепте."""

    model = IngredientInRecipe
    extra = 1
    min_num = 1


class TagRecipeInline(admin.TabularInline):
    """Админка тегов рецептов."""

    model = TagRecipe
    extra = 1
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиента."""

    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""

    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    inlines = (IngredientInRecipeInline, TagRecipeInline)
    list_display = ('id', 'name', 'author', 'text', 'image', 'cooking_time')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    @admin.display(description='Количество добавлений в избранное')
    def count_favorite(self, recipe):
        """Метод подсчета общего числа добавлений этого рецепта в избранное."""
        return recipe.favorites.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка списка избранного."""

    list_display = ('user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = ('id', 'user', 'author', 'created')
    list_filter = ('user',)
    search_fields = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка списка покупок."""

    list_display = ('user', 'recipe', 'id')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'
