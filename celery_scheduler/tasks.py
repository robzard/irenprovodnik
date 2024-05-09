import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import logging
import utils.telegram_bot as tg

from db.requests import get_latest_successful_payments

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def my_daily_task():
    payments = await get_latest_successful_payments()
    logging.info(f'len_payments: {len(payments)}')
    for payment in payments:
        logging.info(f'user_id: {payment.user_id}')
        await tg.subscription_expired(payment.user_id)
    logging.info("Выполнение задачи: %s", datetime.now())


# Создаем планировщик
scheduler = AsyncIOScheduler()


# Получаем текущее время
now = datetime.now()
minute = now.minute + 1  # Настроим запуск на следующую минуту
if minute == 60:
    minute = 0  # Обрабатываем переход через час

# Добавляем задачу, которая будет выполняться в ближайшую минуту
scheduler.add_job(my_daily_task, 'cron', hour=12, minute=10)
# scheduler.add_job(my_daily_task, 'interval', minutes=1)

# Запускаем планировщик
scheduler.start()

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
