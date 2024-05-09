import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging
import utils.telegram_bot as tg

from db.requests import get_users_subscription_expired, set_subscription_false

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def my_daily_task():
    users = await get_users_subscription_expired()
    logging.info(f'users_payments: {len(users)}')
    for user in users:
        logging.info(f'user_id: {user.user_id}')
        await set_subscription_false(user)
        await tg.subscription_expired(user.user_id)
    logging.info("Выполнение задачи: %s", datetime.now())


# Создаем планировщик
scheduler = AsyncIOScheduler()

# scheduler.add_job(my_daily_task, 'cron', hour=13, minute=1)
scheduler.add_job(my_daily_task, 'interval', minutes=1)

# Запускаем планировщик
scheduler.start()

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
