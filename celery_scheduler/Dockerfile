FROM python:3.10-buster

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt


CMD celery -A tasks worker --loglevel=info & celery -A tasks beat --loglevel=info
