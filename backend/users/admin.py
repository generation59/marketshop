from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Follow

admin.site.empty_value_display = 'Не задано'


class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    search_fields = (
        'email',
        'username',
    )


User = get_user_model()

admin.site.register(User, UserAdmin)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following',
    )
