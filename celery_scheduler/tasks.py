import logging
import os

from celery import Celery
from celery.schedules import crontab

from db.requests import get_latest_successful_payments

redis_url = f'{os.getenv("REDIS_HOST")}://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{os.getenv("REDIS_DB")}'
app = Celery('tasks', broker=redis_url, backend=redis_url)


@app.task
def send_notification():
    result = get_latest_successful_payments()
    for el in result:
        logging.info(el.user_id)


app.conf.beat_schedule = {
    'send-notification-every-day': {
        'task': 'tasks.send_notification',
        'schedule': crontab(hour=16, minute=17),
    },
}
