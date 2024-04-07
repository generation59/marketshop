from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingRecipe,
    Tag
)
from users.serializers import CustomUserSerializer

User = get_user_model()


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True
    )
    name = serializers.StringRelatedField(
        source='ingredient.name', read_only=True
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
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
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request is not None and (
                request.user.is_authenticated
                and obj.is_favorited.all().filter(user=request.user).exists())
                )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request is not None and (
                request.user.is_authenticated
                and obj.is_in_shopping_cart.all().
                filter(user=request.user).exists())
                )


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        allow_empty=False,
        error_messages={
            'required': 'Необходимо указать хотя бы один тег.',
            'does_not_exist': 'Выбранный тег не существует.',
            'incorrect_type': 'Неправильный тип данных для этого поля.',
            'not_a_list': 'Укажите список тегов.'
        }
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        required=True,
        allow_empty=False,
        error_messages={
            'required': 'Необходимо указать хотя бы один ингредиент.',
            'does_not_exist': 'Выбранный ингредиент не существует.',
            'incorrect_type': 'Неправильный тип данных для этого поля.',
            'not_a_list': 'Укажите список ингредиентов.'
        }
    )
    image = Base64ImageField(
        required=True,
        error_messages={
            'required': 'Необходимо добавить изображение.'
        }
    )
    cooking_time = serializers.IntegerField(
        required=True,
        min_value=settings.MIN_COOKING_TIME,
        max_value=settings.MAX_COOKING_TIME,
        error_messages={
            'required': 'Укажите время приготовления.',
            'min_value': 'Минимальное время приготовления - '
                         f'{settings.MIN_COOKING_TIME}.',
            'max_value': 'Максимальное время приготовления - '
                         f'{settings.MAX_COOKING_TIME}.'
        }
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        error_messages = {
            'required': 'Обязательное поле.',
            'invalid': 'Недопустимое значение.'
        }

    def update_or_create_recipe_ingredients(self, recipe, ingredients):
        ingredients = [
            RecipeIngredient(
                ingredient_id=ingredient.get('id').id,
                recipe=recipe,
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.update_or_create_recipe_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        self.update_or_create_recipe_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    def validate_image(self, value):
        if not value:
            raise ValidationError(self.error_messages['required'])
        return value

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise ValidationError('Нельзя добавлять одинаковые теги!')
        return value

    def validate(self, data):
        if not data.get('tags') or not data.get('ingredients'):
            raise ValidationError(self.error_messages['missing_fields'])
        ingredients_id = [
            ingredient.get('id') for ingredient in data.get('ingredients')
        ]
        if len(ingredients_id) != len(set(ingredients_id)):
            raise ValidationError('Нельзя добавлять одинаковые ингредиенты!')
        return data


class FavoriteShoppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteShoppingSerializerMixin(serializers.ModelSerializer):

    def to_representation(self, instance):
        return FavoriteShoppingSerializer(
            instance.recipe, context=self.context
        ).data

    def validate(self, data):
        if self.Meta.model.objects.filter(
                user=data.get('user'), recipe=data.get('recipe')
        ).exists():
            raise ValidationError('Рецепт уже добавлен.')
        return data


class FavoriteRecipeSerializer(FavoriteShoppingSerializerMixin):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')


class ShoppingRecipeSerializer(FavoriteShoppingSerializerMixin):
    class Meta:
        model = ShoppingRecipe
        fields = ('user', 'recipe')
