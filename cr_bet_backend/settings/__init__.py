from .base import *

ENV_TYPE = config('ENV_TYPE', 'local')

if ENV_TYPE == 'local':
    from .local import *

if ENV_TYPE == 'dev':
    from .development import *

elif ENV_TYPE == 'live':
    from .production import *

# from virtuleconnect.celery import app as celery_app

# __all__ = ('celery_app',)