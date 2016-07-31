"""
Django settings for graphspace project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ALLOWED_HOSTS = ['*']


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
    'graphs'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware'
)

ROOT_URLCONF = 'graphspace.urls'

WSGI_APPLICATION = 'graphspace.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gsdb',
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

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

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
