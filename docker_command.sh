#!/bin/bash
echo "Starting postgres"
service postgresql start

echo "Starting zookeeper"
service zookeeper start
sleep 2

echo "Starting kafka"
nohup ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties > ~/kafka/kafka.lo$

sleep 2
#cat ~/kafka/kafka.log

echo "Starting redis"
redis-server /etc/redis/redis.conf

echo "Starting elasticsearch"
su elasticsearch && /elasticsearch/bin/elasticsearch -d

sleep 10

echo "Activate virtual env"
source venv/bin/activate 

echo "Migrate"
python manage.py migrate --settings=graphspace.settings.local

echo "Start GraphSpace ... "
python manage.py runserver 0.0.0.0:8000 --settings=graphspace.settings.local
