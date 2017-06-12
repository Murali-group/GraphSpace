from __future__ import absolute_import, unicode_literals

from confluent_kafka import Producer, KafkaError
from django.conf import settings

from json import dumps


def send_message(topic, message):
    settings.KAFKA_PRODUCER.produce(topic, dumps(message))
    settings.KAFKA_PRODUCER.flush()
