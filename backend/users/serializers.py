from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe
from users.models import Follow

User = get_user_model()


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписанных рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CustomUserSerializer(UserSerializer, serializers.ModelSerializer):
    """Сериализатор для пользователей с информацией о подписке."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на другого пользователя."""
        request = self.context.get('request')
        return (request is not None and (
                request.user.is_authenticated
                and obj.followings.filter(user_id=request.user.id).exists())
                )

    def to_representation(self, instance):
        """Добавляет рецепты и возможность изменять их количество в ответе."""
        representation = super().to_representation(instance)

        if self.context.get('request'):
            endpoint = self.context.get('request').build_absolute_uri()
            if 'subscribe' in endpoint or 'subscriptions' in endpoint:
                recipes_limit = (self.context.get('request').
                                 query_params.get('recipes_limit'))
                recipes = instance.recipes.all()
                if recipes_limit and recipes_limit.isdigit():
                    recipes_limit = int(recipes_limit)
                    recipes = recipes[:recipes_limit]

                serializer = SubscribeRecipeSerializer(recipes, many=True)
                representation['recipes'] = serializer.data
                representation['recipes_count'] = recipes.count()
        return representation


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователей."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для функционала подписки на пользователя."""

    class Meta:
        model = Follow
        fields = ('following', 'user')

    def to_representation(self, instance):
        return CustomUserSerializer(
            instance.following, context=self.context
        ).data

    def validate(self, data):
        subscribed = Follow.objects.filter(
            following=data.get('following'), user=data.get('user')
        ).exists()
        if subscribed or data.get('user') == data.get('following'):
            raise ValidationError(
                'Подписка уже существует или '
                'вы пытаетесь подписаться на самого себя.'
            )
        return data
