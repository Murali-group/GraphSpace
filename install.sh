#!/usr/bin/env bash

virtualenv venv
source venv/bin/activate
python setup.py install
python manage.py migrate
