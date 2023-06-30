"""
Django settings for graphspace project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from sqlalchemy.ext.declarative import declarative_base

import os
from elasticsearch import Elasticsearch


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ALLOWED_HOSTS = ['*']

APPEND_SLASH = True

# GLOBAL VALUES FOR DATABASE
DB_FULL_PATH = os.path.join(BASE_DIR, 'graphspace.db')
# DATABASE_LOCATION = 'sqlite:///' + DB_FULL_PATH

# Application definition

INSTALLED_APPS = (
    'analytical',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'applications.users',
    'applications.graphs'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'graphspace.middleware.SQLAlchemySessionMiddleware',
    'graphspace.middleware.GraphSpaceMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'graphspace.urls'

WSGI_APPLICATION = 'graphspace.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'migrate3',
        'USER': 'adb',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

## Old Sqlite Implementation ###
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'graphspace.db')
#     }
# }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Changed from 'UTC'.
TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Email setup
EMAIL_USE_TLS = True
EMAIL_PORT = 587

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = ''

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'graphspace.context_processors.auth',
                'graphspace.context_processors.static_urls',
                'graphspace.context_processors.login_forms',
                'graphspace.context_processors.maintenance',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


LOGIN_REDIRECT_URL = '/'

# for authentication. Since we need to use SQL Alchemy for the ORM, we cannot use the authentication backend automatically provided by Django when using the Django ORM.
AUTHENTICATION_BACKENDS = ('graphs.auth.AuthBackend.AuthBackend',)

# Following the recommendation of the Django tutorial at
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

BASE = declarative_base()
# for connecting with elasticsearch client using hostname and port
ELASTIC_CLIENT = Elasticsearch(['elasticsearch:9200'])

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'applications': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

MAINTENANCE = False
IS_MAINTENANCE_SCHEDULED = False;
MAINTENANCE_START_DATETIME = None;
MAINTENANCE_END_DATETIME = None;
