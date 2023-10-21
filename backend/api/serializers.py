from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Ingredient, IngredientInRecipe, Recipe, Tag,
                            Favorite, ShoppingCart)
from users.models import Subscription, User


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    user = serializers.IntegerField(source='user.id')
    author = serializers.IntegerField(source='author.id')

    class Meta:
        model = Subscription
        fields = ['user', 'author', 'id']

    def validate(self, data):
        request = self.context.get('request')
        user = data['user']['id']
        author = data['author']['id']
        follow_exist = request.user.follower.all().exists()
        if user == author:
            raise serializers.ValidationError(
                {"errors": 'Вы не можете подписаться на самого себя'}
            )
        elif follow_exist:
            raise serializers.ValidationError({"errors": 'Вы уже подписаны'})
        return data

    def create(self, validated_data):
        author = validated_data.get('author')
        author = get_object_or_404(User, pk=author.get('id'))
        user = User.objects.get(id=validated_data["user"]["id"])
        user.follower.create(author=author)
        return validated_data


class UserSerializer(UserCreateSerializer):
    """Сериализатор пользователя."""

    password = serializers.CharField(required=True, write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        model = User

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.follower.filter(author=author.id).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientInRecipe


class AddToIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления количества ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        fields = ('id', 'amount')
        model = IngredientInRecipe


class RecipeMinifieldSerializer(serializers.ModelSerializer):
    """Сериализатор упрощенного отображения модели рецептов."""

    image = Base64ImageField()

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('author',)
        model = Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    author = UserSerializer(default=serializers.CurrentUserDefault())
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipesingredients', many=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.shoppingcart.filter(recipe=obj).exists()
        return False


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = AddToIngredientInRecipeSerializer(
        source='recipesingredients', many=True
    )
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        model = Recipe

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо выбрать ингредиенты!'
            )

        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество не может быть меньше 1!'
                )
        ids = [ingredient['id'] for ingredient in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Данный ингредиент уже есть в рецепте!'
            )
        return ingredients

    def add_ingredients_and_tags(self, tags, ingredients, recipe):
        recipe.tags.set(tags)
        instances = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(instances)
        return recipe

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipesingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe = self.add_ingredients_and_tags(
            tags=tags, ingredients=ingredients, recipe=recipe
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipesingredients')
        instance.tags.clear()
        instance.IngredientInRecipe.clear()
        instance = self.add_ingredients_and_tags(tags, ingredients, instance)
        super().update(instance, validated_data)
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('__all__',)
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавляли это рецепт в избранное.'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
        read_only_fields = ('__all__',)
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже в списке покупок.'
            )
        ]


class ShortRecipeResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class FollowerSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    @staticmethod
    def get_is_subscribed(obj):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()
