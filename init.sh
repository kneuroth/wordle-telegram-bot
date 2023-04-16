#!/bin/bash

ENVIRONMENT=$1

service cron start

#python3 test_init.py

if ["$ENVIRONMENT" == "prod"] then
    gunicorn --certfile=/etc/letsencrypt/live/wordle-bot.kneubots.com/fullchain.pem  --keyfile=/etc/letsencrypt/live/wordle-bot.kneubots.com/privkey.pem --bind 0.0.0.0:8000 app:app
else
    gunicorn --bind 0.0.0.0:8000 app:app
fi

#python3 -m flask run --host=0.0.0.0


