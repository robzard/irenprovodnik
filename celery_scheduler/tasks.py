from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import logging

def my_daily_task():
    print("Выполнение задачи:", datetime.now())
    logging.info("Выполнение задачи:", datetime.now())

# Создаем планировщик
scheduler = BlockingScheduler()

# Получаем текущее время
now = datetime.now()
minute = now.minute + 1  # Настроим запуск на следующую минуту
if minute == 60:
    minute = 0  # Обрабатываем переход через час

# Добавляем задачу, которая будет выполняться в ближайшую минуту
scheduler.add_job(my_daily_task, 'cron', hour=now.hour, minute=minute)

# Запускаем планировщик
scheduler.start()
