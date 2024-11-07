from .base import *
from cr_bet_backend.storage.aws import *

SECRET_KEY = config('SECRET_KEY', 'django-insecure-80+z9u^f)vnd76!m7(*kl04&qlj1^gje7)se$7kx_i^czbwqla')

DEBUG = config('DEBUG', True)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': config('DB_NAME', 'virtuleconnectdb'),
        'USER': config('DB_USER', 'postgres'),
        'PASSWORD': config('DB_PASSWORD', 'Admin@5678'),
        'HOST': config('DB_INSTANCE_HOST', 'localhost'),
        'PORT': config('DB_PORT', 5432),
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
    }
}

CORS_ORIGIN_ALLOW_ALL = True

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv(), default='')
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv(), default='')

CORS_REPLACE_HTTPS_REFERER = True
HOST_SCHEME = 'https://'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 1000000
SECURE_FRAME_DENY = True
SECURE_REFERRER_POLICY = 'origin'
