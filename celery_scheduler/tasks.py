from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import logging

from db.requests import get_latest_successful_payments

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def my_daily_task():
    payments = get_latest_successful_payments()
    logging.info(f'len_payments: {len(payments)}')
    for payment in payments:
        logging.info(f'user_id: {payment.user_id}')
    logging.info("Выполнение задачи: %s", datetime.now())


# Создаем планировщик
scheduler = BlockingScheduler()

# Получаем текущее время
now = datetime.now()
minute = now.minute + 1  # Настроим запуск на следующую минуту
if minute == 60:
    minute = 0  # Обрабатываем переход через час

# Добавляем задачу, которая будет выполняться в ближайшую минуту
# scheduler.add_job(my_daily_task, 'cron', hour=now.hour, minute=minute)
scheduler.add_job(my_daily_task, 'interval', minutes=1)

# Запускаем планировщик
scheduler.start()
