from decouple import config
from google.oauth2 import service_account
import os.path

from ..settings.base import BASE_DIR

# storage settings
GS_BUCKET_NAME = config('GS_BUCKET_NAME')
GS_PROJECT_ID = config('GS_PROJECT_ID')
GS_DEFAULT_ACL = 'publicRead'
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, 'gcpCred.json')
)
# s3 static settings
STATIC_LOCATION = 'static'
STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/{STATIC_LOCATION}/'
STATICFILES_STORAGE = 'cr_bet_backend.storage.storage_backends.GoogleStaticStorage'

# s3 public media settings
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/{PUBLIC_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'cr_bet_backend.storage.storage_backends.GooglePublicMediaStorage'
FILE_UPLOAD_MAX_MEMORY_SIZE = 100000000
FILE_UPLOAD_PERMISSIONS = 0o644
