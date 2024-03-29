import logging
import time

from django.core.management.base import BaseCommand
from pika.exceptions import AMQPConnectionError

from tasks.queue import get_client
from tasks import events  # noqa: registering event handlers

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start listening for events'

    def handle(self, *args, **options):
        while True:
            try:
                rabbit_client = get_client()
                rabbit_client.start_consuming()
            except (AMQPConnectionError, ConnectionResetError, ConnectionRefusedError, OSError) as ex:
                logger.warning('RabbitMQ connection error, retrying in 5 seconds. %s', ex)
                time.sleep(5)
                continue
