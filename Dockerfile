FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN apt-get update 
RUN apt-get install -y chromium
RUN apt-get install -y cron

COPY . .

RUN echo "0 0 * * * /usr/bin/python3 /app/day_end_script.py >> /var/log/cron.log 2>&1" > /etc/cron.d/my-cron

RUN chmod 0644 /etc/cron.d/my-cron

RUN crontab /etc/cron.d/my-cron

RUN pip install gunicorn

ENTRYPOINT ["/bin/bash", "/app/init.sh"]