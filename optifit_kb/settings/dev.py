from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-l3w1l5sh8e@)-1^7bl4%uury1tiz9d_nr+x9ms63j#d$jx58l_"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CSRF_TRUSTED_ORIGINS = [
    "https://kb.optifit.dev",
]

try:
    from .local import *
except ImportError:
    pass
