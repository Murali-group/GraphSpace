from __future__ import absolute_import, unicode_literals

import threading

from applications.notifications import controllers as notifications
from django.conf import settings
from json import loads


class Consumer(threading.Thread):
    """
    Kafka consumer class

    Class object are used to consume notification message to Kafka.
    Currently there can be 2 types of consumer class objects:
    - Owner (for owner notification)
    - Group (for group notification)
    """

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
        consumer_exit = settings.KAFKA_CONSUMER[self.type]
        try:
            for message in settings.KAFKA_CONSUMER[self.type]:
                if message is not None:
                    notify = loads(message.value)
                    self.notification_func[self.type](**notify)
        except KeyboardInterrupt:
            consumer_exit.close()
        finally:
            consumer_exit.close()
