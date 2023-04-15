#!/bin/bash

service cron start

#python3 test_init.py

gunicorn --bind 0.0.0.0:8000 app:app

#python3 -m flask run --host=0.0.0.0


