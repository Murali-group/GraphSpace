from __future__ import absolute_import, unicode_literals

from confluent_kafka import Producer, KafkaError
from django.conf import settings

from graphspace.celery import app


@app.task(ignore_result=True)
def send_message(topic, message):
	prod = Producer({'bootstrap.servers': settings.KAFKA_URL})
	prod.produce(topic, message)
	prod.flush()
	print "hel"

	# Start consumer
	#tasks.consume_message.apply_async((topic))
	app.send_task('applications.notifications.tasks.consume_message', args=[topic])