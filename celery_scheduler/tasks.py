import logging

from db.requests import get_latest_successful_payments

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime


def my_daily_task():
    logging.info("Выполнение задачи:", datetime.now())


# Создаем планировщик
scheduler = BlockingScheduler()

# Добавляем задачу, которая будет выполняться ежедневно в полночь
scheduler.add_job(my_daily_task, 'cron', hour=14, minute=24)

# Запускаем планировщик
scheduler.start()
