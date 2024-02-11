#!/usr/bin/env bash

python setup.py install
python manage.py migrate --settings=graphspace.settings.local
bower install
#Temporary & forced fix untill all the libraries get updated
bower install bootstrap#3.3.7
bower install bootstrap-table#1.11.0