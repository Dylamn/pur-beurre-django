"""
Django settings for purbeurre project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from os import getenv
from pathlib import Path

import sentry_sdk
import dj_database_url
from dotenv import load_dotenv
from purbeurre.utils import strtobool
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load additional environment variables present in a `.env` file.
load_dotenv(dotenv_path=BASE_DIR / 'purbeurre/.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# The application environment.
APP_ENV = getenv('APP_ENV', 'production')

# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = strtobool(getenv('DEBUG', False))

FIXTURE_DIRS = [
    BASE_DIR / "account/tests/fixtures",
    BASE_DIR / "product/tests/fixtures",
    BASE_DIR / "review/tests/fixtures",
]

ALLOWED_HOSTS = [
    '0.0.0.0', 'localhost', '127.0.0.1',
]

ALLOWED_HOSTS.extend(
    getenv('ADDS_ALLOWED_HOSTS').split('|') if getenv('ADDS_ALLOWED_HOSTS') else []
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'algoliasearch_django',

    # Project apps
    'home.apps.HomeConfig',
    'account.apps.AccountConfig',
    'product.apps.ProductConfig',
    'substitute.apps.SubstituteConfig',
    'review.apps.ReviewConfig',
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

if APP_ENV == 'development':  # pragma: no cover Add App(s)/Middleware(s) for the development.
    INSTALLED_APPS.append(*[
        'whitenoise.runserver_nostatic',
    ])

    MIDDLEWARE.append(*[
        # Simplified static file serving.
        # https://warehouse.python.org/project/whitenoise/
        'whitenoise.middleware.WhiteNoiseMiddleware'
    ])

ROOT_URLCONF = 'purbeurre.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'purbeurre.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        ssl_require=strtobool(getenv('DB_SSLMODE', True))
    )
}

# The model to use to represent a User.
AUTH_USER_MODEL = 'account.User'

# Redirect to home URL after login (Default redirect to `/accounts/profile/`)
LOGIN_REDIRECT_URL = '/'

# The login URL.
LOGIN_URL = '/accounts/login'

LOGOUT_REDIRECT_URL = '/'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

if APP_ENV == 'development':  # pragma: no cover
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Algolia settings
# https://www.algolia.com/doc/framework-integration/django/setup/?client=python#setup
ALGOLIA = {
    'APPLICATION_ID': getenv('ALGOLIA_APP_ID'),
    'API_KEY': getenv('ALGOLIA_API_KEY'),
}

# Sentry configuration
sentry_sdk.init(
    dsn=getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # Adjusting this value is recommend in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

if APP_ENV == 'production':  # pragma: no cover
    SECURE_HSTS_SECONDS = int(getenv('HSTS_SECONDS', 31_536_000))
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
