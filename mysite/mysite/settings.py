"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path

from django.urls import reverse_lazy

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
  dsn="https://eb575919f955420c92f33391744b5d66@o4505567246483456.ingest.sentry.io/4505567269683200",
  integrations=[DjangoIntegration()],

  # Set traces_sample_rate to 1.0 to capture 100%
  # of transactions for performance monitoring.
  # We recommend adjusting this value in production.
  traces_sample_rate=1.0,

  # If you wish to associate users to errors (assuming you are using
  # django.contrib.auth) you may enable sending PII data.
  send_default_pii=True
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-hvxn%qq=gyw^4*o2lo1#bw0=wh#ux9s8h!=@c608arf_gz3+^7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "0.0.0.0",
    "127.0.0.1",
]
INTERNAL_IPS = [
    '127.0.0.1',
]

if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS.append("10.0.2.2")
    INTERNAL_IPS.extend(
        # 192.168.1.1
        [ip[: ip.rfind(".")] + ".1" for ip in ips]
    )

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'django.contrib.sitemaps',

    'debug_toolbar',
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    'RSS.apps.RssConfig',

    'blogapp.apps.BlogappConfig',
    'shopapp.apps.ShopappConfig',
    'myauth.apps.MyauthConfig',
    'myapiapp.apps.MyapiappConfig',
]

MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',  # обязательно вначале, перед теми middlewares, которые формируют заголовки
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    # 'django.middleware.cache.FetchFromCacheMiddleware',  # обязательно в конце, после всех middlewares
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHES = {
    "default": {
        # отладочный вариант кэширования? без реального кэширования:
        # "BACKEND": "django.core.cache.backends.dummy.DummyCache",

        # для реального кэширования эти строки раскоментить:
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/var/tmp/django_cache",
        # "LOCATION": "c:/foo/bar",    - for windows
    }
}

CACHE_MIDDLEWARE_SECONDS = 200


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'uploads/'

# if u would like to use custom interaction with file system
# DEFAULT_FILE_STORAGE =

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = reverse_lazy("myauth:about-me")
LOGIN_URL = reverse_lazy("myauth:login")


# для дебагинга:
LOGFILE_NAME = BASE_DIR / 'log.txt'
# LOGFILE_SIZE = 400
LOGFILE_SIZE = 1 * 1024 * 1024
LOGFILE_COUNT = 3
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'logfile': {
            # 'class': 'logging.handlers.TimedRotatingFileHandler',  # класс для ротирования ло-файлов по времени
            'class': 'logging.handlers.RotatingFileHandler',  # класс для ротирования лог-файлов по размеру
            'filename': LOGFILE_NAME,
            'maxBytes': LOGFILE_SIZE,
            'backupCount': LOGFILE_COUNT,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': [
            'console',
            'logfile',
        ],
        'level': 'DEBUG',  # В такой конфигурации будут выводиться логи всепх уровней. Если указать здесь INFO, будут
        # показаны только логи уровня INFO и выше. Самый нижний (debug) уровень видно не будет.
    }
}


# # for logging requests to database in console on DEBUG=True
# LOGGING = {
#     'version': 1,
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         }
#     },
# }


# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_SCHEMA_CLASS": 'drf_spectacular.openapi.AutoSchema',
}


SPECTACULAR_SETTINGS = {
    "TITLE": "My Site Project API",
    "DESCRIPTION": "My site with shop app and custom auth",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}