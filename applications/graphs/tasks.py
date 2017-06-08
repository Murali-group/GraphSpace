from __future__ import absolute_import, unicode_literals

from confluent_kafka import Producer, KafkaError
from django.conf import settings

from graphspace.celery import app as celery_app


@celery_app.task(ignore_result=True)
def send_message(topic, message):
    prod = Producer({'bootstrap.servers': settings.KAFKA_URL})
    prod.produce(topic, message)
    prod.flush()

    # Start consumer
    celery_app.send_task(
        'applications.notifications.tasks.consume_message', args=[topic])
