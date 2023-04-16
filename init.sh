#!/bin/bash

service cron start

#python3 test_init.py

echo $ENVIRONMENT

if [ "$ENVIRONMENT" == "prod" ]; then
    echo "Running with https"
    gunicorn --certfile=fullchain.pem  --keyfile=privkey.pem --bind 0.0.0.0:443 app:app
else
    echo "Running without https" 
    gunicorn --bind 0.0.0.0:8000 app:app
fi

#python3 -m flask run --host=0.0.0.0


