from django.core.management.base import BaseCommand

from tasks.queue import get_client
from tasks import events  # noqa: registering event handlers


class Command(BaseCommand):
    help = 'Start listening for events'

    def handle(self, *args, **options):
        rabbit_client = get_client()
        rabbit_client.start_consuming()
