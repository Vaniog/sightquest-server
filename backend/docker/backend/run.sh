#!/bin/bash

python manage.py collectstatic --noinput
python manage.py migrate
gunicorn -b 0.0.0.0:8000 backend.wsgi:application