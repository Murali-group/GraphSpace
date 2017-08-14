#!/bin/bash
echo "Pull changes"
cd /GraphSpace
git stash 
git pull

echo "Copy configurations"
yes | cp -rf /GraphSpace/docker_config/elasticsearch/elasticsearch.yml /elasticsearch/config/elasticsearch.yml
yes | cp -rf /GraphSpace/docker_config/redis/redis.conf /redis/redis.conf
yes | cp -rf /GraphSpace/docker_config/kafka/server.properties /kafka/config/server.properties
#yes | cp /GraphSpace/docker_config/supervisord/graphspace.conf /etc/supervisor/conf.d/

echo "Starting postgres"
service postgresql start

echo "Starting zookeeper"
service zookeeper start

echo "Sleeping for 5 seconds"
sleep 5

echo "Starting kafka"
> /kafka/kafka.log
nohup /kafka/bin/kafka-server-start.sh /kafka/config/server.properties > /kafka/kafka.log 2>&1 &

echo "Sleeping for 2 seconds"
sleep 2

echo "Starting redis"
mkdir /GraphSpace/redis
redis-server /redis/redis.conf

echo "Creating logs directory"
mkdir logs
mkdir data
> debug.log

echo "Starting elasticsearch"
su - elasticsearch -c '/elasticsearch/bin/elasticsearch -d'

echo "Create virtual env"
virtualenv venv

echo "Activate venv"
. venv/bin/activate

echo "Install dependency"
pip install -r requirements.txt
bower install --allow-root

cp graphspace/settings/docker.py graphspace/settings/production.py

cd /
echo "Changing permissions"
chmod -R 777 /GraphSpace

echo "Sleeping for 10 seconds"
sleep 10

echo "Activate virtual env"
cd ./GraphSpace && source venv/bin/activate 

echo "Migrate"
python manage.py migrate --settings=graphspace.settings.production

echo "Start supervisor ... "
supervisord -n -c '/GraphSpace/docker_config/supervisord/graphspace.conf'
