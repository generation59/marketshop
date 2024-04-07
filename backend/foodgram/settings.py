import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 3600
MIN_AMOUNT = 1
MAX_AMOUNT = 10000
COLOR_MAX_LENGTH = 7
PECIPE_NAME_MAX_LENGTH = 200
USER_NAME_MAX_LENGTH = 150
USER_EMAIL_MAX_LENGTH = 254
NUM_OF_WORDS_OF_NAME = 3
NUM_OF_WORDS_OF_TEXT = 10
PAGINATION_PAGE_SIZE = 6

USE_SQLITE = os.getenv('USE_SQLITE', 'False') == 'true'

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', get_random_secret_key())

DEBUG = 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
    'colorfield',

    'users.apps.UsersConfig',
    'api.apps.ApiConfig',
    'recipes.apps.RecipesConfig',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES_DIR = BASE_DIR / 'templates'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'foodgram'),
            'USER': os.getenv('POSTGRES_USER', 'foodgram_user'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', ''),
            'PORT': os.getenv('DB_PORT', 5432)
        }
    }

AUTH_USER_MODEL = 'users.CreateUser'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'api.utils.page_not_found',

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'api.pagination.PageSizeNumberPagination',
    'PAGE_SIZE': PAGINATION_PAGE_SIZE,

}

DJOSER = {
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'user': ['api.permissions.IsOwnerOrReadOnly'],
        'user_list': ['rest_framework.permissions.AllowAny'],
    },
    'LOGIN_FIELD': 'email',
    'SERIALIZERS': {
        'user': 'users.serializers.CustomUserSerializer',
        'user_create': 'users.serializers.CustomUserCreateSerializer',
        'current_user': 'users.serializers.CustomUserSerializer',
        'user_list': 'users.serializers.CustomUserSerializer',
    }
}

""" Language code English 'en-us'
    Language code Russian 'ru-RU'"""
LANGUAGE_CODE = 'ru-RU'

""" Time zone English 'UTC'
    Time zone Russian 'Europe/Moscow'"""
TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/app/media/'
MEDIA_ROOT = BASE_DIR / 'media'
