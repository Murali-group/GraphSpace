from __future__ import absolute_import, unicode_literals

import threading

from applications.notifications import controllers as notifications
from django.conf import settings
from confluent_kafka import Consumer, KafkaError

from json import loads


class Consumer(threading.Thread):
    daemon = True

    def run(self):
        running = True
        while running:
            message = settings.KAFKA_CONSUMER.poll(timeout=5)
            if message and message.value():
                notify = loads(message.value())
                notify['type'] = 'owner'
                notifications.add_notification(**notify)
            elif message and message.error().code() != KafkaError._PARTITION_EOF:
                # Message ended
                running = False
        return
