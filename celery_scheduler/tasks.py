import logging
import os

from celery import Celery
from celery.schedules import crontab

redis_url = f'{os.getenv("REDIS_HOST")}://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{os.getenv("REDIS_DB")}'
app = Celery('tasks', broker=redis_url, backend=redis_url)


@app.task
def send_notification():
    # Ваш асинхронный код для отправки уведомления
    print("Sending notification...")
    logging.info("Sending notification...")


app.conf.beat_schedule = {
    'send-notification-every-day': {
        'task': 'tasks.send_notification',
        # 'schedule': crontab(hour=0, minute=0),
        'schedule': 1.0,
    },
}
