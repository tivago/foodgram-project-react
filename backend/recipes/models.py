from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveIntegerField,
    SlugField,
    TextField,
    UniqueConstraint
)

User = get_user_model()


class Tag(Model):
    """Тэги для рецептов."""
    
    name = CharField('Название', max_length=200)
    color = CharField('Цвет в HEX', max_length=7)
    slug = CharField('Слаг', max_length=200)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'
    
    
class Ingredient(Model):
    """Ингридиенты для рецепта."""
    name = CharField('Название', max_length=200)
    measurement_unit = CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'
    

class Recipe(Model):
    """Модель для рецептов."""
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Теги',
        related_name='tags'
    )
    name = CharField('Название', max_length=200)
    text = TextField('Описание')
    ingredients = ManyToManyField(
        'CountOfIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    image = ImageField('Картинка')
    cooking_time = PositiveIntegerField(
        'Время приготовления',
        )

    author = ForeignKey(
        User,
        on_delete=SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pk',)

    def __str__(self):
        return f'{self.name} ({self.author})'