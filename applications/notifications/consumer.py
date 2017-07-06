from __future__ import absolute_import, unicode_literals

import threading

from applications.notifications import controllers as notifications
from django.conf import settings
from confluent_kafka import Consumer, KafkaError

from json import loads

import traceback


class Consumer(threading.Thread):
    daemon = True
    type = "owner"  # defaults to 'owner' type notification
    notification_func = {
        "owner": notifications.add_owner_notification,
        "group": notifications.add_group_notification
    }

    def __init__(self, type):
        super(Consumer, self).__init__()
        self.type = type

    def run(self):
        running = True
        consumer_exit = settings.KAFKA_CONSUMER[self.type]
        try:
            while running:
                message = settings.KAFKA_CONSUMER[self.type].poll(0)
                #print message
                # timeout=settings.KAFKA_CONSUMER_POLL_TIMEOUT
                if message is not None and message.value():
                    print message.value()
                    notify = loads(message.value())
                    self.notification_func[self.type](**notify)
                """
                elif message is not None and message.error().code() != KafkaError._PARTITION_EOF:
                    # Message ended
                    running = False
            
                """
        except KeyboardInterrupt:
            consumer_exit.close()
        finally:
            consumer_exit.close()

        return consumer_exit.close()
