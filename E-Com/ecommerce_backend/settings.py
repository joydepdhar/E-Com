from pathlib import Path
import os
import cloudinary
import environ
from django.core.exceptions import ImproperlyConfigured

# Define BASE_DIR before using it
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
# Ensure .env values override shell values in local development.
os.environ.setdefault('DJANGO_ENV', 'development')
environ.Env.read_env(BASE_DIR / '.env', override=True)

if os.environ['DJANGO_ENV'].lower() == 'development':
    os.environ['DATABASE_URL'] = 'postgres://ecommerce_user:12312312@localhost:5432/ecommerce_db'

env = environ.Env(
    DEBUG=(bool, False)
)

# Environment separation: development is HTTP-friendly by default, while
# production enables HTTPS-only security controls.
DJANGO_ENV = env('DJANGO_ENV', default='development').lower()
if DJANGO_ENV not in {'development', 'production'}:
    raise ImproperlyConfigured("DJANGO_ENV must be either 'development' or 'production'.")

IS_PRODUCTION = DJANGO_ENV == 'production'

# SECRET_KEY is always supplied from the environment; it is never hardcoded.
SECRET_KEY = env('SECRET_KEY')

# Production must explicitly run without Django debug mode. Development keeps
# DEBUG enabled by default so local HTTP development continues to work.
DEBUG = env.bool('DEBUG', default=not IS_PRODUCTION)
if IS_PRODUCTION and DEBUG:
    raise ImproperlyConfigured('DEBUG must be False when DJANGO_ENV is production.')

# Hosts and trusted CSRF origins remain deployment-specific environment values.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# Redirect production HTTP requests to HTTPS. Disabled locally to avoid
# requiring certificates for the development server.
SECURE_SSL_REDIRECT = IS_PRODUCTION

# Send session and CSRF cookies only over HTTPS in production.
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION

# Trust the HTTPS scheme reported by a TLS-terminating proxy such as Render.
# Keep this unset locally, where requests reach Django directly.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if IS_PRODUCTION else None

# Enable one-year HSTS in production only. This instructs browsers to use HTTPS
# for this domain and its subdomains, and permits inclusion in HSTS preload lists.
SECURE_HSTS_SECONDS = 31_536_000 if IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION
SECURE_HSTS_PRELOAD = IS_PRODUCTION



# CORS
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
])

# Application definition
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'django_filters',
    'corsheaders',
    'cloudinary',

    # Your apps
    'user_app',
    'store',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'store.logging_context.RequestIDMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # static files middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # add your templates dirs here if any
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce_backend.wsgi.application'

# Database configuration (default to sqlite3)
# DATABASES = {
#     'default': env.db(default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
# }
# Database
DATABASES = {
    "default": env.db()
}

# Keep connections alive
DATABASES["default"]["CONN_MAX_AGE"] = 600

# Enable SSL only for cloud PostgreSQL
if "neon.tech" in DATABASES["default"]["HOST"]:
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "require",
    }
# Custom user model
AUTH_USER_MODEL = 'user_app.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Credentials used by Product.image and CustomUser.profile_picture.
CLOUDINARY_CLOUD_NAME = env('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = env('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = env('CLOUDINARY_API_SECRET')

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

# CloudinaryField performs its own upload. Other files use Django's local
# backend, while collected static/admin files are served by WhiteNoise.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Do not turn API responses into 500 errors when a newly installed package has
# static assets that are not present in an older collected-static manifest.
# WhiteNoise will fall back to the unhashed asset URL until collectstatic runs.
WHITENOISE_MANIFEST_STRICT = False

# Django REST Framework with JWT authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_VERSIONING_CLASS': 'ecommerce_backend.versioning.APIVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ('v1',),
    'VERSION_PARAM': 'version',
    # Collection endpoints use page-number pagination with a default size of 20.
    'DEFAULT_PAGINATION_CLASS': 'store.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'EXCEPTION_HANDLER': 'store.exceptions.custom_exception_handler',
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'store.logging_context.RequestIDFilter',
        },
    },
    'formatters': {
        'standard': {
            'format': (
                '%(asctime)s %(levelname)s %(name)s '
                'request_id=%(request_id)s %(message)s'
            ),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['request_id'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'store': {
            'handlers': ['console'],
            'level': env('STORE_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'store.payments': {
            'handlers': ['console'],
            'level': env('PAYMENTS_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'store.orders': {
            'handlers': ['console'],
            'level': env('ORDERS_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'authentication': {
            'handlers': ['console'],
            'level': env('AUTH_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}
