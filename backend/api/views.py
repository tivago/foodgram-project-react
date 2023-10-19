from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from users.models import Subscription, User
from recipes.models import (Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from .pagination import LimitPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, ShortRecipeResponseSerializer,
                          RecipeMinifieldSerializer, RecipePostSerializer,
                          RecipeSerializer, SubscriptionsSerializer,
                          TagSerializer, UserSerializer, FavoriteSerializer,
                          ShoppingCartSerializer, SubscriptionsToSerializer)


class MainUserViewSet(UserViewSet):
    """Вьюсет для пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination

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
        methods=['POST'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        user = self.request.user
        data = {"author": author.id, "user": user.id}
        serializer = SubscriptionsToSerializer(
            data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        user = self.request.user
        following = get_object_or_404(Subscription, user=user, author=author)
        following.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    permission_class = (IsAuthorOrReadOnly, IsAuthenticated,)
    pagination_classes = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    serializer_class = RecipeSerializer, RecipeMinifieldSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipePostSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = (
            ShoppingCart.objects.filter(user=request.user)
            .values(
                'recipe__ingredients__name',
                'recipe__ingredients__measurement_unit',
            )
            .annotate(amount=Sum('recipe__recipesingredients__amount'))
            .order_by('recipe__ingredients__name')
        )
        page = ['Список покупок:\n--------------']
        for index, recipe in enumerate(shopping_cart, start=1):
            page.append(
                f'{index}. {recipe["recipe__ingredients__name"]} - '
                f'{recipe["amount"]} '
                f'{recipe["recipe__ingredients__measurement_unit"]}.',
            )
        response = HttpResponse(page, content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment;filename=shopping_cart.csv'
        )
        return response

    @staticmethod
    def post_for_shopping_cart_and_favorite(request, pk, serializer_req):
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer_req(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer_data = ShortRecipeResponseSerializer(recipe)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_for_shopping_cart_and_favorite(request, pk, location, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'Рецепт уже удален из {location}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['post'], detail=True)
    def favorite(self, request, pk):
        return self.post_for_shopping_cart_and_favorite(
            request, pk, FavoriteSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_for_shopping_cart_and_favorite(
            request, pk, 'избранного', Favorite
        )

    @action(methods=['post'], detail=True,)
    def shopping_cart(self, request, pk):
        return self.post_for_shopping_cart_and_favorite(
            request, pk, ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_for_shopping_cart_and_favorite(
            request, pk, 'списка покупок', ShoppingCart
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientSearchFilter
