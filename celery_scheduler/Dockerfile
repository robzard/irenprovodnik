FROM python:3.10-buster

WORKDIR /app

# Установка необходимых пакетов для компиляции и обновление pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libffi-dev python3-dev && \
    pip install --upgrade pip

COPY . /app

RUN pip install -r requirements.txt


CMD celery -A tasks worker --loglevel=info & celery -A tasks beat --loglevel=info
