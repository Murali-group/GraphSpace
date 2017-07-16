from __future__ import absolute_import, unicode_literals

from django.conf import settings
from json import dumps

from graphspace.signals import send_notification


def send_message(topic, message):
    # Send notification through websockets
    send_notification(
        topic=topic,
        notification=message
    )
    settings.KAFKA_PRODUCER.produce(topic, dumps(message))
    settings.KAFKA_PRODUCER.flush()
