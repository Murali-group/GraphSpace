#!/bin/bash
service postgresql start

service zookeeper start
sleep 2
nohup ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties > ~/kafka/kafka.lo$

sleep 2
cat ~/kafka/kafka.log

redis-server /etc/redis/redis.conf
su elasticsearch && /elasticsearch/bin/elasticsearch -d

sleep 10

cd GraphSpace && source venv/bin/activate 

python manage.py migrate --settings=graphspace.settings.local

python manage.py runserver 0.0.0.0:8000 --settings=graphspace.settings.local