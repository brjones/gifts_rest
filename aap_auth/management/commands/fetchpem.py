from django.core.management.base import BaseCommand
from aap_auth.auth import AAPAcess

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Fetching AAP PEM certificate")

        AAPAcess().fetchPEM()
