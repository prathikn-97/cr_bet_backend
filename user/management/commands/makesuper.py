from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    @staticmethod
    def handle(*args, **options):
        User = get_user_model()
        if not User.objects.filter(username='superadmin').exists():
            User.objects.create_superuser("admin@celestrous.us", "Admin@5678", username="superadmin")
