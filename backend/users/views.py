from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Follow
from users.serializers import FollowSerializer

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """Обрабатывает запрос на получение, создание, редактирование,
    удаления пользователей и подписок."""

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Получаем данные пользователя сделавшего запрос."""
        return super().me(request)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Получаем подписки принадлежащие пользователю."""
        subscribed_users = []
        subscribes = request.user.subscribers.all()
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(subscribes, request)

        for subscription in result_page:
            subscribed_user = subscription.following
            subscribed_users.append(subscribed_user)

        serializer = self.get_serializer(
            subscribed_users, many=True
        )

        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """Функция для создания или удаления подписки."""
        following = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'following': id, 'user': request.user.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not Follow.objects.filter(
            following=following, user=request.user,
        ).exists():
            raise ValidationError('Вы не подписаны на этого пользователя.')
        Follow.objects.filter(user=request.user, following=following).delete()
        return Response('Подписка удалена.', status.HTTP_204_NO_CONTENT)
