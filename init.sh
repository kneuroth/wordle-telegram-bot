#!/bin/bash

service cron start

#python3 test_init.py

gunicorn --bind :$PORT app:app

#python3 -m flask run --host=0.0.0.0


