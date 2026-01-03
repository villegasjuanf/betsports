FROM python:3.11-bullseye

WORKDIR /app

RUN apt-get update && apt-get -y install cron libpq5 && apt-get clean

COPY requirements.txt requirements.txt
COPY . /app
WORKDIR /app/betsports

RUN pip install --upgrade pip &&\
 pip install --no-cache-dir -r ../requirements.txt &&\
 pip install gunicorn