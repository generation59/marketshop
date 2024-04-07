from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeSearchFilter
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (
    CreateUpdateRecipeSerializer,
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingRecipeSerializer,
    TagSerializer
)
from api.utils import download_file
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShoppingRecipe,
    Tag
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ('delete', 'get', 'patch', 'post')
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter

    def create_or_delete_related_record(
            self, request, pk, related_model, serializer
    ):
        """Функция для создания или удаления связанной с рецептом записи."""
        if request.method == 'POST':
            serializer = serializer(
                data={'user': request.user.id, 'recipe': pk},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        recipe = get_object_or_404(Recipe, pk=pk)
        if not related_model.objects.filter(
                user=request.user, recipe=recipe
        ).exists():
            raise ValidationError('Такого рецепта нет в списке.')
        related_model.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(
            'Рецепт удалён из избранного.', status.HTTP_204_NO_CONTENT
        )

    def get_serializer_class(self):
        """Выбирает сериализатор, в зависимости от метода запроса."""
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateUpdateRecipeSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Добвляем или удаляем рецепт из избранного."""
        return self.create_or_delete_related_record(
            request,
            pk,
            FavoriteRecipe,
            FavoriteRecipeSerializer
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавляем или удаляем рецепт из списка покупок."""
        return self.create_or_delete_related_record(
            request,
            pk,
            ShoppingRecipe,
            ShoppingRecipeSerializer
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Получить и скачать список покупок в файле."""
        purchases_list = self.queryset.filter(
            is_in_shopping_cart__user=request.user
        ).values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).order_by(
            'ingredients__name'
        ).annotate(
            amount=Sum('recipe_ingredients__amount')
        )
        shopping_list = '\n'.join(
            '- {}: {} {}.'.format(
                ingredient.get('ingredients__name'),
                ingredient.get('amount'),
                ingredient.get('ingredients__measurement_unit')
            )
            for ingredient in purchases_list
        )
        return download_file(shopping_list, 'shopping_list.txt')
