from django_filters import AllValuesMultipleFilter, CharFilter, FilterSet

from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(FilterSet):
    """Фильтр для ингредиентов."""

    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeSearchFilter(FilterSet):
    """Фильтр для рецептов."""

    tags = AllValuesMultipleFilter(
        label='tags',
        field_name='tags__slug'
    )
    is_favorited = CharFilter(method='is_favorited_filter')
    is_in_shopping_cart = CharFilter(method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = (
            'author', 'tags', 'is_favorited', 'is_in_shopping_cart'
        )

    def is_favorited_filter(self, queryset, name, value):
        """Получаем рецепты которые находятся в избранном."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                is_favorited__user=self.request.user
            )
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        """Получаем рецепты которые находятся в списке покупок."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                is_in_shopping_cart__user=self.request.user
            )
        return queryset
