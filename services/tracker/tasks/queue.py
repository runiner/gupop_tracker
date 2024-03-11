import json
import logging
from functools import lru_cache, wraps
from typing import Callable

import pika
from pika.exchange_type import ExchangeType

EXCHANGE = 'events'
TRACKER_IN_QUEUE = 'events_in_tracker'
TRACKER_IN_DLX_QUEUE = 'dlx.events_in_tracker'

logger = logging.getLogger(__name__)


class Client:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='rabbitmq',
                virtual_host='rabbit',
                credentials=pika.credentials.PlainCredentials('rabbituser', 'rabbitpass')
            )
        )
        self.channel = self.connection.channel()
        self._handlers: dict[str: Callable] = {}
        self._setup_schema()

    def _setup_schema(self):
        self.channel.exchange_declare(EXCHANGE, exchange_type=ExchangeType.fanout, durable=True)
        self.channel.queue_declare(TRACKER_IN_DLX_QUEUE, durable=True)
        self.channel.queue_declare(TRACKER_IN_QUEUE, durable=True, arguments={"dead-letter-exchange": "dlx.events_in_tracker"})
        self.channel.queue_bind(TRACKER_IN_QUEUE, EXCHANGE)
        self.channel.basic_consume(queue=TRACKER_IN_QUEUE, on_message_callback=self._on_message)

    def _on_message(self, ch, method, properties, body):
        logger.info(f" [x] Received {body.decode()}")

        message = json.loads(body)
        if message['name'] in self._handlers:
            self._handlers[message['name']](message)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def add_handler(self, event_name: str):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            self._handlers[event_name] = wrapper
            return wrapper
        return decorator

    def start_consuming(self):
        self.channel.start_consuming()

    def publish_message(self, routing_key: str, message: dict):
        self.channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(message).encode(),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            )
        )


@lru_cache
def get_client():
    return Client()
