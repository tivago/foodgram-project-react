from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Subscription, Tag)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, PasswordSerializer,
                          RecipeMinifieldSerializer, RecipePostSerializer,
                          RecipeSerializer, SubscriptionsSerializer,
                          TagSerializer, UserSerializer)


class CreateUserViewSet(UserViewSet):
    """Вьюсет для пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    http_method_name = (
        'get',
        'post',
        'put',
        'patch',
        'delete',
    )

    @action(
        detail=False,
        url_path='set_password',
        methods=['POST'],
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        user = request.user
        context = {'request': request}
        serializer = PasswordSerializer(data=request.data, context=context)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'status': 'Пароль установлен!'})
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request, pk=None):
        if request.method == ['GET']:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        obj = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            obj, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user == author:
                return Response(
                    data={'detail': 'Нельзя подписываться на себя!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    data={'detail': 'Вы уже подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            subscribe = Subscription.objects.filter(user=user, author=author)
            if not subscribe.exists():
                return Response(
                    data={'detail': 'Вы не подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    permission_class = (IsAuthorOrReadOnly,)
    pagination_classes = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        else:
            return RecipePostSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user.id
        ).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(amount=Sum('recipe__recipesingredients__amount'))
        shopping_cart = ['Список покупок:\n--------------']
        for position, ingredient in enumerate(ingredients, start=1):
            shopping_cart.append(
                f'\n{position}. {ingredient["recipe__ingredients__name"]}:'
                f' {ingredient["amount_sum"]}'
                f'({ingredient["recipe__ingredients__measurement_unit"]})'
            )
        response = HttpResponse(shopping_cart, content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment;filename=shopping_cart.csv'
        )
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientSearchFilter


class FavoriteViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для избранных рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeMinifieldSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            return Response(
                data={'detail': 'Этот рецепт уже есть в избранном!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if not favorite.exists():
            return Response(
                data={'detail': 'Вы не подписаны на этот рецепт!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(
            f'Рецепт {favorite} удален из избранного у пользователя'
            f' {request.user}',
            status=status.HTTP_204_NO_CONTENT,
        )


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет для списка покупок."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeMinifieldSerializer
    permission_classes = (
        IsAdminOrReadOnly,
        IsAuthorOrReadOnly,
        IsAuthenticated,
    )

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                data={'detail': 'Рецепт уже есть в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if not cart.exists():
            return Response(
                data={'detail': 'Рецепта еще нет в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.delete()
        return Response(
            f'Рецепт {cart} удален из списка покупок у пользователя'
            f' {request.user}',
            status=status.HTTP_204_NO_CONTENT,
        )
