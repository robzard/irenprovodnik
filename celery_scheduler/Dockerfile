FROM python:3.10

WORKDIR /app

COPY . /app

# Установите необходимые пакеты
RUN apt-get update && apt-get install -y gcc libffi-dev

# Теперь попробуйте установить backports.zoneinfo
RUN pip install backports.zoneinfo

RUN pip install -r requirements.txt


CMD celery -A tasks worker --loglevel=info & celery -A tasks beat --loglevel=info
