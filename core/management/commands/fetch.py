from core.views import github
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("Refreshing contributions")
        github()
        self.stdout.write("Refreshing contributions done.")
