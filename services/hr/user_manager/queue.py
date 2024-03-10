import json
from functools import lru_cache

import pika
from pika.exchange_type import ExchangeType

EXCHANGE = 'events'


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
        self._setup_schema()

    def _setup_schema(self):
        self.channel.exchange_declare(EXCHANGE, exchange_type=ExchangeType.fanout, durable=True)

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
