from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import (
    CharField,
    Model,
)
MINIMAL_INGREDIENST_AMOUNT = 1
MAX_INGREDIENTS_AMOUNT = 50
MINIMAL_COOKING_TIME = 1
MAX_COOCKING_TIME = 420

User = get_user_model()


class Tag(Model):
    """Тэги для рецептов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
        help_text='Введите название тега',
    )
    color = ColorField(
        default='#FF0000',
        max_length=200,
        verbose_name='Цвет тега',
        unique=True,)
    slug = CharField(
        max_length=200,
        unique=True,
        verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Ingredient(Model):
    """Ингридиенты для рецепта."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            )
        ]

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(Model):
    """Модель для рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MINIMAL_COOKING_TIME,
                f'минимальное время приготовления {MINIMAL_COOKING_TIME} мин.',
            ),
            MaxValueValidator(
                MAX_COOCKING_TIME,
                f'максимальное время приготовления {MAX_COOCKING_TIME} мин.',
            )
        ],
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег рецепта',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Необходимые ингредиенты',
        help_text='Выберете необходимые ингредиенты',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания рецепта',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.name} - {self.author}'


class IngredientInRecipe(models.Model):
    """Модель количества ингредиентов в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='ingredientinrecipes',
        verbose_name='Ингредиенты рецепта',
        help_text='Выберите ингредиенты рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipesingredients',
        verbose_name='Рецепт',
        help_text='Выберите рецепт',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество ингредиента',
        validators=[
            MinValueValidator(
                MINIMAL_INGREDIENST_AMOUNT,
                f'укажите количество не менее {MINIMAL_INGREDIENST_AMOUNT}',
            ),
            MaxValueValidator(
                MAX_INGREDIENTS_AMOUNT,
                f'слишком много ингредиентов {MAX_INGREDIENTS_AMOUNT}',
            )
        ],
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe} -{self.ingredient}, {self.amount}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Избранный пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorite'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    """Модель корзины."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Рецепт в списке покупок',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('-user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]
