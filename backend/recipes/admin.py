from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingRecipe,
    Tag
)

admin.site.empty_value_display = 'Не задано'


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 0
    min_num = 1


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'get_short_name',
        'author',
        'get_short_text',
        'cooking_time',
        'created_at',
        'get_favorite_count',
        'image_tag',
    )
    search_fields = ('name',)
    list_filter = ('author', 'tags',)
    inlines = (RecipeTagInline, RecipeIngredientInline)

    @admin.display(description='Название')
    def get_short_name(self, obj):
        """Получаем начальные слова названия рецепта."""
        return " ".join(obj.name.split()[:settings.NUM_OF_WORDS_OF_NAME])

    @admin.display(description='Описание')
    def get_short_text(self, obj):
        """Получаем начальные слова описания рецепта."""
        return (
            f'{" ".join(obj.text.split()[:settings.NUM_OF_WORDS_OF_TEXT])} ...'
        )

    @admin.display(description='Изображение')
    def image_tag(self, obj):
        """Получаем изображение рецепта."""
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="50" />'.format(obj.image.url)
            )
        return 'Не найдено'

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        """Сколько раз рецепт добавлен в избранное."""
        return FavoriteRecipe.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'get_short_name',
        'measurement_unit',
    )
    search_fields = ('name',)

    @admin.display(description='Название')
    def get_short_name(self, obj):
        """Получаем начальные слова названия ингредиента."""
        return " ".join(obj.name.split()[:settings.NUM_OF_WORDS_OF_NAME])


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingRecipe)
class ShoppingRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
