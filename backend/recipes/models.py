from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator)
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Тег', max_length=settings.PECIPE_NAME_MAX_LENGTH, unique=True,
    )
    color = models.CharField(
        max_length=settings.COLOR_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{3,6})$',
                message='Значение не цвет в формате HEX!'
            )
        ],
        default='#E26C2D',
        verbose_name='Цвет',
        help_text='Введите например, #E26C2D',
    )
    slug = models.SlugField(
        'Слаг', max_length=settings.PECIPE_NAME_MAX_LENGTH, unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент', max_length=settings.PECIPE_NAME_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        'Еденица измерения',
        max_length=settings.PECIPE_NAME_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name="unique_title_measurement_unit_pair"
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        'Название',
        max_length=settings.PECIPE_NAME_MAX_LENGTH
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Удерживайте Ctrl для выбора нескольких вариантов'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Теги',
        help_text='Удерживайте Ctrl для выбора нескольких вариантов'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время',
        default=settings.MIN_COOKING_TIME,
        validators=[
            MaxValueValidator(settings.MAX_COOKING_TIME),
            MinValueValidator(settings.MIN_COOKING_TIME)
        ]
    )
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='Тег')

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        default_related_name = 'tag_recipe'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name="unique_recipe_tag_pair"
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        default=settings.MIN_AMOUNT,
        validators=[
            MaxValueValidator(settings.MAX_AMOUNT),
            MinValueValidator(settings.MIN_AMOUNT)
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeUserBase(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('recipe__name',)
        abstract = True

    def __str__(self):
        return f'{self.user} {self.recipe}'


class FavoriteRecipe(RecipeUserBase):
    class Meta(RecipeUserBase.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'is_favorited'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name="favorite_unique_user_recipe_pair"
            )
        ]


class ShoppingRecipe(RecipeUserBase):
    class Meta(RecipeUserBase.Meta):
        verbose_name = 'Ингредиент для покупки'
        verbose_name_plural = 'Ингредиенты для покупки'
        default_related_name = 'is_in_shopping_cart'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name="shopping_unique_user_recipe_pair"
            )
        ]
