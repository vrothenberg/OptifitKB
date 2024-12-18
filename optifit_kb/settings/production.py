from .base import *

# Get the SECRET_KEY from the environment
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-secret-key")  # Replace the fallback with something safe but not ideal for prod

# Set DEBUG to False for production
DEBUG = False

# Define the allowed hosts for your application
ALLOWED_HOSTS = ["kb.optifit.dev"]

# Configure CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    "https://kb.optifit.dev",
]

# Secure cookie settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# HTTP Strict Transport Security (HSTS)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Redirect HTTP to HTTPS
SECURE_SSL_REDIRECT = True

# Email settings for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "your-smtp-server"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@example.com"
EMAIL_HOST_PASSWORD = "your-email-password"

# Static and Media file settings
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs/django.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}

try:
    from .local import *
except ImportError:
    pass
