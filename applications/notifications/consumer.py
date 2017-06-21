from __future__ import absolute_import, unicode_literals

import threading

from applications.notifications import controllers as notifications
from django.conf import settings
from confluent_kafka import Consumer, KafkaError

from json import loads


class OwnerConsumer(threading.Thread):
    daemon = True

    def run(self):
        running = True
        while running:
            message = settings.KAFKA_OWNER_CONSUMER.poll(
                timeout=settings.KAFKA_CONSUMER_POLL_TIMEOUT)
            if message is not None and message.value():
                notify = loads(message.value())
                notifications.add_owner_notification(**notify)
            elif message is not None and message.error().code() != KafkaError._PARTITION_EOF:
                # Message ended
                running = False
        return
