#!/usr/bin/env bash

python setup.py install
python manage.py migrate --settings=graphspace.settings.local
bower install
