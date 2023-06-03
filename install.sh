#!/usr/bin/env bash

python setup.py install
python manage.py migrate --settings=graphspace.settings.local
bower install
bower install bootstrap#3.3.7
bower install bootstrap-table#1.11.0