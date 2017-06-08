from __future__ import absolute_import, unicode_literals
from graphspace.celery import app
from confluent_kafka import Consumer, KafkaError
from django.conf import settings

@app.task(ignore_result=True)
def consume_message(topic):
	con = Consumer({'bootstrap.servers': settings.KAFKA_URL, 'group.id': 'graphspace', 'default.topic.config': {'auto.offset.reset': 'smallest'}})
	con.subscribe([topic])
	running = True
	while running:
		message = con.poll(timeout=10)
		if not message.error():
			# run specific function for the topic
			print message.value()
		elif message.error().code() != KafkaError._PARTITION_EOF:
			# Message ended
			running = False
	con.close()
