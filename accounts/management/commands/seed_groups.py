from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

ROLE_NAMES = ["worker", "keeper", "supervisor", "admin"]

class Command(BaseCommand):
    help = "Create default role groups"

    def handle(self, *args, **options):
        created = 0
        for name in ROLE_NAMES:
            _, is_created = Group.objects.get_or_create(name=name)
            created += int(is_created)
        self.stdout.write(self.style.SUCCESS(f"Done. Created {created} groups."))