#!/bin/bash
echo "Sleeping for 10 seconds"
sleep 10

echo "Activate virtual env"
cd ./GraphSpace && source venv/bin/activate 

echo "Migrate"
python manage.py migrate --settings=graphspace.settings.production

echo "Start supervisor ... "
supervisord -n -c '/GraphSpace/docker_config/supervisord/graphspace.conf'
