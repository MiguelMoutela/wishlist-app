from django.core.management.base import BaseCommand, CommandError
from web.utils import send_christmas_email


class Command(BaseCommand):
    help = 'Send Christmas email'

    def handle(self, *args, **options):
        try:
            send_christmas_email()
        except:
            raise CommandError('Something is wrong.')
