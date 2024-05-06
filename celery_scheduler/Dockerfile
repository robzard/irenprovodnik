FROM python:3.8-slim

# Установка рабочей директории
WORKDIR /app

# Копирование файлов Python зависимостей и установка их
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копирование остальных файлов проекта
COPY . .

# Запуск Celery worker и Celery Beat в одном контейнере
CMD celery -A tasks worker --loglevel=info & celery -A tasks beat --loglevel=info
