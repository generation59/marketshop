from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class CreateUser(AbstractUser):
    email = models.EmailField(
        max_length=settings.USER_EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=settings.USER_NAME_MAX_LENGTH, unique=True,
        verbose_name='Ник-нейм пользователя',
        validators=[
            RegexValidator(
                r'^[\w.@+-]+\Z',
                'Вы не можете зарегистрировать пользователя с таким именем.'
            ),
            RegexValidator(
                '^me$',
                'Вы не можете зарегистрировать пользователя с таким именем.',
                inverse_match=True
            ),
        ]
    )
    first_name = models.CharField(
        max_length=settings.USER_NAME_MAX_LENGTH, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=settings.USER_NAME_MAX_LENGTH, verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=settings.USER_NAME_MAX_LENGTH, verbose_name='Пароль'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        CreateUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        CreateUser,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'), name='unique_user_and_following'
            ),
            models.CheckConstraint(
                name='subscriber_is_not_following',
                check=~models.Q(user_id=models.F("following_id")),
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.following}'
