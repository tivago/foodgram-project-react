#!/bin/bash -x
python manage.py migrate --noinput
python manage.py collectstatic 
cp -rf /app/static/. /static/static/ 
gunicorn --bind 0.0.0.0:8000 foodgram.wsgi