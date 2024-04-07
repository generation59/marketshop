from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import FoodgramUserViewSet

router_v1 = DefaultRouter()

router_v1.register('users', FoodgramUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    re_path('^auth/', include('djoser.urls.authtoken')),
]
