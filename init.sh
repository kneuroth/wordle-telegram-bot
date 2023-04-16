#!/bin/bash

ENVIRONMENT=$1

service cron start

#python3 test_init.py

if ["$ENVIRONMENT" == "prod"] then
    gunicorn --certfile=server.crt --keyfile=server.key --bind 0.0.0.0:8000 app:app
else
    gunicorn --bind 0.0.0.0:8000 app:app
fi

#python3 -m flask run --host=0.0.0.0


