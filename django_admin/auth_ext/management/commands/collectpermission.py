from django.core.management import BaseCommand
from auth_ext.models.permission import PermissionDetector


class Command(BaseCommand):
    def handle(self, *args, **options):
        result = PermissionDetector().auto_discover_permissions()
        print(*[
            f'{k}: {v}' for k, v in result.items()
        ], sep='\n')
