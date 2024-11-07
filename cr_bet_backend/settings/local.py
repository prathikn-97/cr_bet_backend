from .base import *


SECRET_KEY = 'django-insecure-80+z9u^f)vnd76!m7(*kl04&qlj1^gje7)se$7kx_i^czbwqla'

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_INSTANCE_HOST'),
        'PORT': config('DB_PORT'),
        'TEST': {
            'MIRROR': 'default',
        },
        # 'OPTIONS': {
        #     'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        # },
    }
}
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'csdb',
#         'USER': 'postgres',
#         'PASSWORD': 'Admin@5678',
#         'HOST': 'localhost',
#         'PORT': 5432
#     }
# }

CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000"
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CELERY SETTINGS

CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'

MYSQL_SENSITIVE_COLLATION = 'ascii_bin'  
DB_CASE_SENSITIVE_COLLATION  = {'db_collation': MYSQL_SENSITIVE_COLLATION}
