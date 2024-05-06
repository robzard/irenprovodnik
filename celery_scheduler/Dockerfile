FROM python:3.8-slim

WORKDIR /celery_scheduler

# Копируем только папку celery_scheduler
COPY . .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Запускаем Celery worker и beat
CMD celery -A tasks worker --loglevel=info & celery -A tasks beat --loglevel=info
