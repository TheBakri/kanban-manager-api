from datetime import timedelta
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import os
import sys

try:
    import environ
    HAS_ENVIRON = True
except Exception:  # pragma: no cover - package not installed
    environ = None
    HAS_ENVIRON = False

BASE_DIR = Path(__file__).resolve().parent.parent

if HAS_ENVIRON:
    env = environ.Env(
        DEBUG=(bool, True),
    )
    ENV_FILE = BASE_DIR / ".env"
    if ENV_FILE.exists():
        env.read_env(ENV_FILE)
else:
    # Minimal fallback implementation so settings can evaluate values
    # without django-environ. Uses os.environ directly and provides a
    # subset of the Env API used in this settings file.
    class DummyEnv:
        def __call__(self, key, default=None):
            return os.environ.get(key, default)

        def bool(self, key, default=False):
            val = os.environ.get(key)
            if val is None:
                return default
            return str(val).lower() in ("1", "true", "yes")

        def list(self, key, default=None):
            val = os.environ.get(key)
            if val is None:
                return default or []
            return [p.strip() for p in val.split(",") if p.strip()]

        def str(self, key, default=None):
            return os.environ.get(key, default)

        def int(self, key, default=0):
            val = os.environ.get(key)
            if val is None:
                return default
            try:
                return int(val)
            except Exception:
                return default

        def db(self, key, default=None):
            # Return raw DATABASE_URL string; DATABASES fallback used below.
            return os.environ.get(key, default)

    env = DummyEnv()

SECRET_KEY = env("SECRET_KEY", default="change-me")
DEBUG = env.bool("DEBUG", default=True)


ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"] if DEBUG else [])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "rest_framework_simplejwt.token_blacklist",
    "users",
    "teams",
    "projects",
    "boards",
    "tasks",
    "comments",
    "activity",
    "notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

if HAS_ENVIRON:
    DATABASES = {
        "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
    }
else:

    db_url = env.db("DATABASE_URL", default=None)
    if db_url:

        from urllib.parse import urlparse

        parsed = urlparse(db_url)
        db_name = parsed.path[1:] if parsed.path else ""
        db_user = parsed.username
        db_pass = parsed.password
        db_host = parsed.hostname
        db_port = parsed.port
        scheme = parsed.scheme
        if scheme.startswith("postgres"):
            engine = "django.db.backends.postgresql"
        elif scheme.startswith("mysql"):
            engine = "django.db.backends.mysql"
        else:
            engine = "django.db.backends.sqlite3"

        DATABASES = {
            "default": {
                "ENGINE": engine,
                "NAME": db_name,
                "USER": db_user,
                "PASSWORD": db_pass,
                "HOST": db_host,
                "PORT": db_port,
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(BASE_DIR / "db.sqlite3"),
            }
        }

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://redis:6379/1"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
}


REST_FRAMEWORK.update({
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": env.str("THROTTLE_ANON_PER_MIN", default="10/min"),
        "user": env.str("THROTTLE_USER_PER_MIN", default="100/min"),
    },
})

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Rotate refresh tokens and enable blacklisting. This is helpful to reduce the
# impact of a leaked refresh token.
SIMPLE_JWT.update({
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
})

SPECTACULAR_SETTINGS = {
    "TITLE": "Kanban Manager API",
    "DESCRIPTION": "API documentation for all backend modules",
    "VERSION": "1.0.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL", default=False)


CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# Trusted origins for CSRF validation (Django 4+ requires scheme + host)
# Example: CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://127.0.0.1:8000"]
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://localhost"]) 

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_TIMEOUT = env.int("EMAIL_TIMEOUT", default=10)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER or "no-reply@kanban.local")

if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ImproperlyConfigured("EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be True")

if not DEBUG and EMAIL_BACKEND.endswith("smtp.EmailBackend"):
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        raise ImproperlyConfigured(
            "EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set in production when using SMTP backend"
        )

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/0")
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_BEAT_SCHEDULE = {
    "check_due_soon_tasks_every_hour": {
        "task": "notifications.tasks.check_due_soon_tasks",
        "schedule": timedelta(hours=1),
    }
}


CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=DEBUG)
CELERY_TASK_EAGER_PROPAGATES = env.bool("CELERY_TASK_EAGER_PROPAGATES", default=True)

# Ensure Celery runs eagerly when Django test suite is invoked without explicit env vars
if "test" in sys.argv:
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True


SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=not DEBUG)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# policy (like no-referrer) is safer.
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade" if DEBUG else "no-referrer"
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=not DEBUG)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000 if not DEBUG else 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)


if not DEBUG and SECRET_KEY == "change-me":
    raise ImproperlyConfigured("SECRET_KEY must be set to a secure value in production (via .env)")
