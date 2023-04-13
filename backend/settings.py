import datetime
import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
import django
from decouple import config
from django.utils.translation import gettext_lazy as _
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = os.path.join(BASE_DIR, 'static_content')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG",cast=bool)

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'yoozify.herokuapp.com'
]

GOOGLE_ANALYTICS = {
    'google_analytics_id': config("GOOGLE_ANALYTICS_ID"),
}

# Application definition

INSTALLED_APPS = [
    'baton',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    'rest_framework',
    'rest_framework.authtoken',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth',
    'dj_rest_auth.registration',

    'corsheaders',
    'crispy_forms',
    'tinymce',
    'django_filters',
    'google_analytics',
    'drf_yasg',

    # my apps
    'Accounts',
    'ContactUs',
    'SupportTicket',
    'Blog',


    'baton.autodiscover',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # 'Accounts.middleware.RestrictNonAdminUsersMiddleware',
]


ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
# ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")


# Database
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination',

    'DEFAULT_FILTER_BACKENDS':('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PARSER_CLASSES':[
        'rest_framework.parsers.JSONParser',
        'Blog.parser.MultiPartJSONParser',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

SWAGGER_SETTINGS = {

     'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema',
     'DEFAULT_FIELD_INSPECTORS': [
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.ReferencingSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
     ],
     'DEFAULT_FILTER_INSPECTORS': [
        'drf_yasg.inspectors.CoreAPICompatInspector',
     ],
     'DEFAULT_PAGINATOR_INSPECTORS': [
        'drf_yasg.inspectors.DjangoRestResponsePagination',
        'drf_yasg.inspectors.CoreAPICompatInspector',
     ],

    'USE_SESSION_AUTH': False,  # add Django Login and Django Logout buttons, CSRF token to swagger UI page
    # 'LOGIN_URL': getattr(django.conf.settings, 'LOGIN_URL', None),  # URL for the login button
    # 'LOGOUT_URL': getattr(django.conf.settings, 'LOGOUT_URL', None),  # URL for the logout button

    # Swagger security definitions to include in the schema;
    # see https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#security-definitions-object
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'VALIDATOR_URL': '',
    'OPERATIONS_SORTER': None,
    'TAGS_SORTER': None,
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': False,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'model',
    'DEFAULT_MODEL_DEPTH': 3,
}

REDOC_SETTINGS = {

    'LAZY_RENDERING': True,
    'HIDE_HOSTNAME': False,
    'EXPAND_RESPONSES': 'all',
    'PATH_IN_MIDDLE': False,
}

REST_AUTH_SERIALIZERS = {
    'REGISTER_SERIALIZER':'Accounts.serializers.CustomRegisterSerializer',
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'Accounts.auth_backends.CustomAuthenticationBackend',
]


ACCOUNT_ADAPTER = 'Accounts.adapter.CustomUserAccountAdapter'


AUTH_USER_MODEL = 'Accounts.User'

SITE_ID = 1
LOGIN_REDIRECT_URL = '/'

CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://yoozify.herokuapp.com",
]

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

LANGUAGES = (
    ('fa', _("Persian")),
    ('en', _("English")),
)

TIME_ZONE = 'Iran'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(CONTENT_DIR, 'assets')
]
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(CONTENT_DIR, 'static_root')

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(CONTENT_DIR, 'media_root')

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

BATON = {
    'SITE_HEADER':_("Yoozify"),
    'SITE_TITLE':_("Yoozify"),
    'SHOW_MULTIPART_UPLOADING':True,
    'COLLAPSABLE_USER_AREA':False,
    'GRAVATAR_DEFAULT_IMAGE':'blank',
}

JSL_DJANGO_SITEMAP_SETTINGS = {
	"ENABLE": True,
	"FETCH_URL_FROM": "pattern",
	"INCLUDE_APPS": ("ALL",)
}

BASE_URL = 'http://yoozify.herokuapp.com'


KAVEH_NEGAR_API_KEY = config("KAVEH_NEGAR_API_KEY")