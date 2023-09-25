from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Subscription, Tag, TagRecipe)


class IngredientInRecipeInline(admin.TabularInline):
    """Админка ингредиентов в рецепте."""

    model = IngredientInRecipe
    extra = 1


class TagRecipeInline(admin.TabularInline):
    """Админка тегов рецептов."""

    model = TagRecipe
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиента."""

    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""

    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    inlines = (IngredientInRecipeInline, TagRecipeInline)
    list_display = ('id', 'name', 'author', 'text', 'image', 'cooking_time')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def count_favorite(self, obj):
        """Метод подсчета общего числа добавлений этого рецепта в избранное."""
        return Favorite.objects.filter(recipe=obj).count()

    count_favorite.short_description = 'Количество добавлений в избранное'


class FavoriteAdmin(admin.ModelAdmin):
    """Админка списка избранного."""

    list_display = ('user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class SubscriptionAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = ('id', 'user', 'author', 'created')
    list_filter = ('user',)
    search_fields = ('user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка списка покупок."""

    list_display = ('user', 'recipe', 'id')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
