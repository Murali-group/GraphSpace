#!/bin/bash
echo "Pull changes"
cd /GraphSpace
git stash
git pull

echo "Copy configurations"
yes | cp -rf /GraphSpace/docker_config/elasticsearch/elasticsearch.yml /elasticsearch/config/elasticsearch.yml
yes | cp -rf /GraphSpace/docker_config/redis/redis.conf /redis/redis.conf

echo "Starting postgres"
service postgresql start

echo "Sleeping for 5 seconds"
sleep 5

echo "Starting redis"
mkdir /GraphSpace/redis
redis-server /redis/redis.conf

# echo "Creating logs directory"
# mkdir logs
# mkdir data
# > debug.log

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

echo "Running Daphne"
daphne -b localhost -p 8002 graphspace.asgi:channel_layer &

echo "Sleeping for 5 seconds"
sleep 5

echo "Running server"
python manage.py runworker

echo "Enjoy browsing GraphSpace"