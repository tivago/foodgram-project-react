from django.db import transaction
from django.forms import ValidationError
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import Subscription, User
from recipes.models import (Ingredient, IngredientInRecipe, Recipe, Tag,
                            Favorite, ShoppingCart)


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = SubscriptionsSerializer(
            instance,
            context=context
        )
        return serializer.data

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя!'
            )
        return data


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = User

    def validate(self, data):
        user = self.context['request'].user
        if data['author'] == user:
            raise ValidationError('Нельзя подписываться на самого себя!')
        return data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Subscription.objects.filter(
            user=request.user.is_authenticated,
            author=obj
        ).exists()

    def get_recipes(self, author):
        queryset = author.recipes.all()
        return RecipeMinifieldSerializer(queryset, many=True).data

    def get_recipes_count(self, author):
        return author.recipes.all().count()


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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.follower.filter(author=obj).exists()
        )


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

    def get_is_favorited(self, recipe):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and request.user.favorites.filter(recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.shoppingcart.filter(recipe=recipe).exists()
        )


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
        print(ingredients)
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
        recipe.save()
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
        instance.save()
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
