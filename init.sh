#!/bin/bash

service cron start

#python3 test_init.py

echo $ENVIRONMENT

if [ "$ENVIRONMENT" == "prod" ]; then
    echo "Running with https"
    gunicorn --certfile=/etc/letsencrypt/live/wordle-bot.kneubots.com/fullchain.pem  --keyfile=/etc/letsencrypt/live/wordle-bot.kneubots.com/privkey.pem --bind 0.0.0.0:443 app:app
else
    echo "Running without https" 
    gunicorn --bind 0.0.0.0:8000 app:app
fi

#python3 -m flask run --host=0.0.0.0


